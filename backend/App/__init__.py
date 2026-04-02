from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # 注册data蓝图
    from .routes.geodata import bp as geodata_bp
    app.register_blueprint(geodata_bp)
    
    # 注册predict蓝图
    from .routes.predict import bp as predict_bp
    app.register_blueprint(predict_bp)
    
    # 注册geeinfo蓝图
    from .routes.geeinfo import bp as geeinfo_bp
    app.register_blueprint(geeinfo_bp)
    
    # 注册imgAct蓝图
    from .routes.imgAct import bp as imgAct_bp
    app.register_blueprint(imgAct_bp)
    
    # 注册imgcAct蓝图
    from .routes.imgcAct import bp as imgcAct_bp
    app.register_blueprint(imgcAct_bp)
    
    from .routes.aichat import bp as aichat_bp
    app.register_blueprint(aichat_bp)
    
    
    return app