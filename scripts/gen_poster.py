import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.font_manager as fm
from matplotlib.font_manager import FontProperties

font_path = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
font_prop = FontProperties(fname=font_path)

fig, ax = plt.subplots(figsize=(16, 24))
fig.patch.set_facecolor('#0f111a') # Deep dark blue/black
ax.set_xlim(0, 100)
ax.set_ylim(0, 140)
ax.axis('off')

# Title
ax.text(50, 136, "2026 年 4 月 · 新番鉴赏指南", ha='center', va='center', fontsize=42, color='#00f2ff', fontweight='bold', fontproperties=font_prop)
ax.text(50, 129, "深度挖掘 | 30+ 部作品 | 避雷与看点 | by boku", ha='center', va='center', fontsize=16, color='#aaaaaa', fontproperties=font_prop)

# Helper functions
def draw_category_header(y, text, color):
    ax.text(2, y+1, text, fontsize=22, color=color, fontweight='bold', fontproperties=font_prop)
    ax.plot([2, 98], [y-1.5, y-1.5], color=color, linewidth=3, alpha=0.5)

def draw_row(y, name, studio, pros, cons):
    rect = patches.Rectangle((2, y-3), 96, 7, facecolor='#15192b', edgecolor='#2a344d', linewidth=1)
    ax.add_patch(rect)
    ax.text(4, y+0.5, name, fontsize=16, color='#ffffff', fontweight='bold', fontproperties=font_prop)
    ax.text(4, y-1.5, studio, fontsize=12, color='#667788', fontproperties=font_prop)
    ax.text(35, y+0.5, "✅ " + pros[:28] + ("..." if len(pros)>28 else ""), fontsize=14, color='#00ff88', fontproperties=font_prop)
    ax.text(72, y+0.5, "⚠️ " + cons[:28] + ("..." if len(cons)>28 else ""), fontsize=14, color='#ff4444', fontproperties=font_prop)

y = 120

# 1. 霸权
draw_category_header(y, "🔥 霸权预定 (Must Watch)", '#00f2ff')
y -= 8
items = [
    ("魔法帽的工作室", "WIT STUDIO", "画面绝美，WIT 炫技", "节奏较慢，慢热型"),
    ("黄泉使者", "BONES 骨头社", "牛姨原作，打斗稳健", "铺垫期长，需耐心"),
    ("Re0 第四季", "White Fox", "剧情深度，心理博弈", "极度虐心，胃药警告"),
    ("杀手青春", "动画工房", "反差搞笑，OP/ED 精良", "主角大叔出场时间少"),
    ("实力至上主义 4", "Lerche", "路哥智商碾压，爽文", "剧情套路化，公式严重"),
    ("朱音落语", "Telecom", "文化底蕴，声优演绎", "有文化门槛，不懂难 Get"),
    ("日本三國", "SIGNAL.MD", "色彩美学极佳，OP 好听", "原作慢热，需耐心"),
]
for n, s, p, c in items:
    draw_row(y, n, s, p, c)
    y -= 7.5

# 2. 宝藏
y -= 5
draw_category_header(y, "💎 宝藏/冷门 (Hidden Gems)", '#00ff88')
y -= 8
items = [
    ("公鸡斗士", "Dwarf Studio", "肌肉公鸡主角，硬核搞笑", "画风清奇，第一集可能劝退"),
    ("冻結地球", "未知", "音乐神级，庵野/小岛推荐", "人设劝退，剧情转折好猜"),
    ("大贤者里德尔", "未知", "老练主角重生，反杀爽文", "设定复杂，信息量大"),
    ("Candy Caries", "WIT STUDIO", "画风诡异独特，实验短片", "电波系，挑人，像恐怖片"),
    ("转生贩卖机 3", "未知", "变成贩卖机在迷宫卖东西", "异世界套路变种，看多易腻"),
    ("怪奇物语：85 年", "未知", "复古科幻恐怖，80 年代风", "恐怖氛围铺垫慢，非突脸"),
    ("左撇子艾伦", "未知", "左撇子视角运动番，新奇", "制作可能贫穷，作画崩"),
]
for n, s, p, c in items:
    draw_row(y, n, s, p, c)
    y -= 7.5

# 3. 阴间
y -= 5
draw_category_header(y, "🌶️ 阴间/争议 (Spicy & Weird)", '#ff4444')
y -= 8
items = [
    ("女骑士成蛮族新娘", "寿门堂", "跨文化纯爱喜剧，女主可爱", "部分平台付费限定，名字像雷番"),
    ("婚姻剧毒", "未知", "名字就叫剧毒，可能病娇", "心理承受弱者慎入，致郁"),
    ("木头风纪委员和迷你裙 JK", "未知", "古板男 vs 时尚女，反差", "剧情单薄，基本看人设"),
    ("雾尾粉丝后援会", "未知", "暗恋博弈，扭曲感，胃痛", "纠结，非甜宠番，胃疼"),
    ("弱弱老师", "未知", "老师身材好，福利满满", "剧情弱，卖肉搞笑"),
    ("淫狱团地", "未知", "尺度极大，设定炸裂", "San 值狂掉，剧情离谱"),
    ("这样高大的女孩", "未知", "专注于体型差 (巨大娘)", "受众极窄，非好此口者尴尬"),
    ("女神《肋骨》", "未知", "名字长是看点，搞笑", "制作一般，可能为泡面番"),
]
for n, s, p, c in items:
    draw_row(y, n, s, p, c)
    y -= 7.5

# 4. 日常
y -= 5
draw_category_header(y, "📺 续作/日常 (Standard)", '#888888')
y -= 8
items = [
    ("天使大人 2", "project No.9", "全程发糖，放松首选", "剧情薄弱，日常撒狗粮"),
    ("异世界悠闲农家 2", "ZERO-G", "种田流慢生活，治愈", "剧情平淡，无冲突"),
    ("入间同学入魔了 4", "BN Pictures", "欢乐向恶魔校园", "套路重复，新鲜感下降"),
    ("出租女友 5", "TMS", "胃疼恋爱，修罗场", "男主优柔寡断，高血压"),
    ("Dr.STONE 3 季 3", "TMS", "硬核科学复活人类", "完结篇节奏可能赶"),
    ("小鲨鱼去郊游 2", "ENGI", "治愈系泡面番，可爱", "时长短，没剧情"),
]
for n, s, p, c in items:
    draw_row(y, n, s, p, c)
    y -= 7.5

# Footer
y -= 5
ax.text(50, y, "⚠️ 免责声明：评价基于网络评分与观众反馈，具有主观性。番剧质量可能随集数播出发生变化。", 
        ha='center', va='center', fontsize=12, color='#555555', fontproperties=font_prop)

plt.tight_layout()
plt.savefig('/home/ubuntu/.hermes/Anime_Poster_Cyberpunk.png', dpi=200, bbox_inches='tight')
print("Poster generated successfully!")
