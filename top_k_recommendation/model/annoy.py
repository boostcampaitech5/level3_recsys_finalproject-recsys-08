from tqdm import tqdm
from annoy import AnnoyIndex

def build_annoy(df_biz,args):
    """
    build trees
    """
    length_of_vector = args.d_embed
    num_data = df_biz.shape[0]
    annoy_index = AnnoyIndex(length_of_vector, 'angular')  
    for idx in tqdm(range(num_data)):
        vector = df_biz.iloc[idx]['embedding']
        annoy_index.add_item(idx, vector)
    annoy_index.build(args.n_trees) 
    annoy_index.save('patent_ann.annoy')

class Annoy:
    def __init__(self, args, annoy_index):
        self.n_trees = args.n_trees
        self.n = args.n
        self.d_embed = args.d_embed
        self.annoy_index = annoy_index
        
    def find_annoy(self,vector):
        ann_idx, ann_score = self.annoy_index.get_nns_by_vector(vector, self.n, include_distances=True)
        return ann_idx[::-1],ann_score[::-1]