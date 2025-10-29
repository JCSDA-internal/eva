"""
EVA Transform: reduce
=====================

A small, generic reduction transform that operates on a single DataArray in the
DataCollections and writes the reduced result back into the collection.

1) Fetch a variable from DataCollections (using "Collection::Group::Variable")
2) Optionally mask fill values to NaN so reductions can use `skipna=True`
3) Optionally squeeze `binsZDim` by selecting index 0 (common when binsZDim == 1)
4) Apply a reduction over one or more named dimensions
5) Save the result back to DataCollections under "new name"

Supported operations: "mean", "sum", "min", "max", "std", and "identity"
- "identity" does no reduction, but still applies mask/squeeze if requested.

---------------------------------------------------------------------------
Example YAML
---------------------------------------------------------------------------
transforms:
  - transform: reduce
    source: "ObsMonitor::griddedBins_ombg_stationPressure::mean"
    new name: "ObsMonitor::griddedBins_ombg_stationPressure::mean_cycleAvg"
    op: "mean"
    dims: ["analysisCycle"]
    skipna: true
    squeeze_binsZ: false
    mask_fill: true

# 2-D output directly (no slicing later):
  - transform: reduce
    source: "ObsMonitor::griddedBins_ombg_stationPressure::mean"
    new name: "ObsMonitor::griddedBins_ombg_stationPressure::mean_cycleAvg_2d"
    op: "mean"
    dims: ["analysisCycle"]
    squeeze_binsZ: true
    mask_fill: true
"""

from typing import List, Optional

import xarray as xr

from eva.utilities.logger import Logger
from eva.utilities.config import get
from eva.transforms.transform_utils import split_collectiongroupvariable


def _mask_fill(da: xr.DataArray) -> xr.DataArray:
    """Mask the dataset's _FillValue (if present) to NaN."""
    if da is None:
        return da
    fv = da.attrs.get("_FillValue", None)
    if fv is None and hasattr(da, "encoding"):
        fv = da.encoding.get("_FillValue", None)
    return da.where(da != fv) if fv is not None else da


def reduce(config: dict, data_collections) -> None:
    """
    Reduce a DataArray over named dimensions and store the result back into EVA.

    Parameters
    ----------
    config : dict
        Transform configuration with the following keys:
          - source (str): "Collection::Group::Variable" to read
          - new name (str): "Collection::Group::NewVariable" to write
          - op (str): one of {"mean","sum","min","max","std","identity"}
          - dims (list[str], optional): dims to reduce over (e.g., ["analysisCycle"])
          - skipna (bool, optional, default=True): ignore NaNs in reductions
          - squeeze_binsZ (bool, optional, default=False):
                if True and "binsZDim" present, select index 0
          - mask_fill (bool, optional, default=True):
                mask `_FillValue` to NaN before reduction
    data_collections : eva.data.data_collections.DataCollections
        EVA DataCollections instance.

    Returns
    -------
    None
        The reduced DataArray is added to DataCollections under "new name".

    Notes
    -----
    - "identity" op is useful to apply mask/squeeze only (no reduction).
    - If `dims` is omitted or empty for reduction ops, the transform reduces over *all* dims.
    - Attributes/coords are preserved by xarray.
    """
    logger = Logger("ReduceTransform")

    # Required fields
    source = get(config, logger, "source")
    new_name = get(config, logger, "new name")
    op = get(config, logger, "op").lower()

    # Optional fields
    dims: Optional[List[str]] = get(config, logger, "dims", default=None)
    skipna: bool = get(config, logger, "skipna", default=True)
    squeeze_bins: bool = get(config, logger, "squeeze_binsZ", default=False)
    mask_fill: bool = get(config, logger, "mask_fill", default=True)

    # Parse source and fetch
    coll, group, var = split_collectiongroupvariable(logger, source)
    da: xr.DataArray = data_collections.get_variable_data_array(coll, group, var)

    if da is None:
        raise ValueError(f"ReduceTransform: source '{source}' not found in DataCollections.")

    # Mask fill value if requested
    if mask_fill:
        da = _mask_fill(da)

    # Optional vertical squeeze (select first vertical bin)
    if squeeze_bins and "binsZDim" in da.dims:
        da = da.isel(binsZDim=0)

    # Normalize dims: None -> all dims for reduction ops
    if op != "identity":
        if dims is None or len(dims) == 0:
            dims = list(da.dims)

    # Dispatch operation
    if op == "mean":
        out = da.mean(dim=dims, skipna=skipna)
    elif op == "sum":
        out = da.sum(dim=dims, skipna=skipna)
    elif op == "min":
        out = da.min(dim=dims, skipna=skipna)
    elif op == "max":
        out = da.max(dim=dims, skipna=skipna)
    elif op == "std":
        out = da.std(dim=dims, skipna=skipna)
    elif op == "identity":
        out = da
    else:
        raise ValueError(f"ReduceTransform: unsupported op '{op}'.")

    # Write back
    out_coll, out_group, out_var = split_collectiongroupvariable(logger, new_name)
    data_collections.add_variable_to_collection(out_coll, out_group, out_var, out)

    logger.info(
        f"ReduceTransform: wrote '{new_name}' "
        f"(op={op}, dims={dims if op!='identity' else 'n/a'}, skipna={skipna}, "
        f"squeeze_binsZ={squeeze_bins}, mask_fill={mask_fill})"
    )
