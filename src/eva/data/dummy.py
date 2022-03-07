from eva.eva_base import EvaBase
import pandas as pd

class Dummy(EvaBase):

    def execute(self):
        data_dict = {'x': [1,2,3,4,5], 'y': [1,2,3,4,5]}
        self.data = pd.DataFrame.from_dict(data_dict)


