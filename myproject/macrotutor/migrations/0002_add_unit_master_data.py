from django.db import migrations

def add_master_data(apps, schema_editor):
    UnitMaster = apps.get_model('macrotutor', 'UnitMaster')
    

    data = [
        # --- 数学 ---
        {'subject': 'MATH', 'grade': 'GRADE_1', 'unit_name': '正の数・負の数'},
        {'subject': 'MATH', 'grade': 'GRADE_1', 'unit_name': '文字と式'},
        {'subject': 'MATH', 'grade': 'GRADE_1', 'unit_name': '方程式'},
        {'subject': 'MATH', 'grade': 'GRADE_1', 'unit_name': '比例と反比例'},
        {'subject': 'MATH', 'grade': 'GRADE_1', 'unit_name': '平面図形'},
        {'subject': 'MATH', 'grade': 'GRADE_1', 'unit_name': '空間図形'},
        {'subject': 'MATH', 'grade': 'GRADE_1', 'unit_name': '資料の活用'},
        
        {'subject': 'MATH', 'grade': 'GRADE_2', 'unit_name': '式の計算'},
        {'subject': 'MATH', 'grade': 'GRADE_2', 'unit_name': '連立方程式'},
        {'subject': 'MATH', 'grade': 'GRADE_2', 'unit_name': '一次関数'},
        {'subject': 'MATH', 'grade': 'GRADE_2', 'unit_name': '平行線と角'},
        {'subject': 'MATH', 'grade': 'GRADE_2', 'unit_name': '図形の合同'},
        {'subject': 'MATH', 'grade': 'GRADE_2', 'unit_name': '三角形と四角形'},
        {'subject': 'MATH', 'grade': 'GRADE_2', 'unit_name': '確率'},
        
        {'subject': 'MATH', 'grade': 'GRADE_3', 'unit_name': '式の展開と因数分解'},
        {'subject': 'MATH', 'grade': 'GRADE_3', 'unit_name': '平方根'},
        {'subject': 'MATH', 'grade': 'GRADE_3', 'unit_name': '二次方程式'},
        {'subject': 'MATH', 'grade': 'GRADE_3', 'unit_name': '関数 $y=ax^2$'},
        {'subject': 'MATH', 'grade': 'GRADE_3', 'unit_name': '相似な図形'},
        {'subject': 'MATH', 'grade': 'GRADE_3', 'unit_name': '円の性質'},
        {'subject': 'MATH', 'grade': 'GRADE_3', 'unit_name': '三平方の定理'},

        # --- 英語 ---
        {'subject': 'ENGLISH', 'grade': 'GRADE_1', 'unit_name': 'Be動詞'},
        {'subject': 'ENGLISH', 'grade': 'GRADE_1', 'unit_name': '一般動詞'},
        {'subject': 'ENGLISH', 'grade': 'GRADE_1', 'unit_name': 'can・命令文'},
        {'subject': 'ENGLISH', 'grade': 'GRADE_1', 'unit_name': '現在進行形'},
        {'subject': 'ENGLISH', 'grade': 'GRADE_1', 'unit_name': '疑問詞'},
        
        {'subject': 'ENGLISH', 'grade': 'GRADE_2', 'unit_name': '未来形・助動詞'},
        {'subject': 'ENGLISH', 'grade': 'GRADE_2', 'unit_name': '不定詞'},
        {'subject': 'ENGLISH', 'grade': 'GRADE_2', 'unit_name': '動名詞'},
        {'subject': 'ENGLISH', 'grade': 'GRADE_2', 'unit_name': '比較'},
        {'subject': 'ENGLISH', 'grade': 'GRADE_2', 'unit_name': '受動態'},
        
        {'subject': 'ENGLISH', 'grade': 'GRADE_3', 'unit_name': '現在完了'},
        {'subject': 'ENGLISH', 'grade': 'GRADE_3', 'unit_name': '関係代名詞'},
        {'subject': 'ENGLISH', 'grade': 'GRADE_3', 'unit_name': '分詞'},
        {'subject': 'ENGLISH', 'grade': 'GRADE_3', 'unit_name': '仮定法'},
    ]
    

    UnitMaster.objects.bulk_create([UnitMaster(**item) for item in data])

class Migration(migrations.Migration):

    dependencies = [
        ('macrotutor', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_master_data),
    ]
