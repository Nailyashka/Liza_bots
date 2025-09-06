from aiogram import Router
from handlers.admin_tools import admin_tools_router
from handlers.admin import admin_router
from handlers.manage_admin import manage_admins_router
from handlers.super_admin import superadmin_router

main_admin = Router()

main_admin.include_router(admin_tools_router)
main_admin.include_router(admin_router)
main_admin.include_router(manage_admins_router)
main_admin.include_router(superadmin_router)