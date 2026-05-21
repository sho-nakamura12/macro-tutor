from django.urls import path
from . import views

app_name = "macrotutor"

urlpatterns = [
    # ==========================================
    # 1. ページ表示・標準的なフォーム送信系
    # ==========================================
    # トップページ（生徒一覧）
    path("", views.student_list, name="student_list"),

    # 生徒関連（追加・詳細・編集・削除）
    path("add_student/", views.create_student_with_units, name="add_student"),
    path("student/<int:pk>/", views.student_detail, name="student_detail"),
    path("student/<int:pk>/edit/", views.edit_student, name="edit_student"),
    path("student/<int:pk>/delete/", views.delete_student, name="delete_student"),

    # 単元追加関連（単体・一括）
    path("student/<int:pk>/add_unit/", views.add_unit, name="add_unit"),
    path("student/<int:pk>/add_units/", views.add_units, name="add_units"),
    
    # 古い同期フォーム用の単元削除（念のため残存）
    path("student/<int:pk>/unit/<int:unit_id>/delete/", views.delete_unit, name="delete_unit"),

    # ==========================================
    # 2. HTMX / AJAX・API系（部分更新・非同期処理）
    # ==========================================
    # マスターデータ検索API
    path("api/unitmaster/", views.unitmaster_api, name="unitmaster_api"),

    # 単元ステータス更新（HTMX）
    path("unit/<int:unit_id>/status/", views.update_unit_status, name="update_unit_status"),

    # 単元削除系（AJAX / 一括リセット）
    path("unit/<int:pk>/delete_ajax/", views.delete_unit_ajax, name="delete_unit_ajax"),
    path("student/<int:pk>/delete_all_units/", views.delete_all_units, name="delete_all_units"),
]