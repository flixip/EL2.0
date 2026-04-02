from flask import Blueprint,jsonify,request
from Aichat.agents import agent001,agent002,agent003

bp = Blueprint('aichat', __name__)

@bp.route('/aiChat', methods=['POST'])
def ai_chat():
    '''
    调用AIChat模型
    预期参数{
        "query":"查询Sentinel-2数据集的id"
    }
    '''
    
    query = request.json.get('query')
    response = agent003.query(query)
    
    return jsonify({'status': 'success','answer': response})
