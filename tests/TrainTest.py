import sys
sys.path.append(r"C:\Users\Administrator\Documents\GitHub\QQ-Bot-And-Tool") 
from service import config
config.initialize()

from service.MatchSys import MatchSys
ms = MatchSys(
        name='teat_sys',
        ltp_model_path=r'C:\Users\Administrator\Documents\GitHub\QQ-Bot-And-Tool\data\LtpModel',
        database_uri='sqlite:///data/db.sqlite3',
        text_vec_model_path=r'C:\Users\Administrator\Documents\GitHub\QQ-Bot-And-Tool\data\model.pkl',
        vector_similarity_rate=0.7,
        most_similar_number=10,
        vector_match_times=5,

    )

