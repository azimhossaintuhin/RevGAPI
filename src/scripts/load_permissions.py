from  pathlib import Path
import json
from src.models.permission import Role, Permission, RolePermission, PermissionModule
from src.config.database import async_session
import asyncio
from sqlalchemy import select

BASE_DIR = Path(__file__).parent.parent
PERMISSIONS_FILE = BASE_DIR / "templates" / "loaders" / "permissions.json"
def load_permissions_from_file(file_path: Path):
    with open(file_path, "r") as file:
        return json.load(file)


async def load_permissions():
    async with async_session() as session:  # FIX

        data = load_permissions_from_file(PERMISSIONS_FILE)

        for module_data in data:

    # 1. Create module
            module = PermissionModule(name=module_data["module"])
            session.add(module)
            await session.flush()

            # 2. Create roles (global, avoid duplicates)
            role_objects = {}

            for role_data in module_data["roles"]:
                role = await session.scalar(
                    select(Role).where(Role.name == role_data["name"])
                )

                if not role:
                    role = Role(
                        name=role_data["name"]
                    )
                    session.add(role)
                    await session.flush()

                role_objects[role.name] = role

            # 3. Create permissions
            for perm_data in module_data["permissions"]:

                perm = Permission(
                    name=perm_data["name"],
                    code=perm_data["code"],
                    description=perm_data["description"],
                    module_id=module.id
                )

                session.add(perm)
                await session.flush()

                # 4. Assign ALL roles in this module to ALL permissions
                for role in role_objects.values():

                    session.add(RolePermission(
                        role_id=role.id,
                        permission_id=perm.id
                    ))

        await session.commit()
    
if __name__ == "__main__":
    asyncio.run(load_permissions())
        