async def get_roles(db, guild):
    data = await db.fetch("SELECT role_id, cookies FROM shop WHERE guild_id = $1", guild.id)

    if len(data) == 0:
        return None

    roles = dict()
    for raw in data:
        role = guild.get_role(raw['role_id'])
        if role:
            roles[role] = raw['cookies']

    roles_list = sorted(roles, key=lambda role: roles[role])
    return {r: roles[r] for r in roles_list}


async def get_inventory(db, user_id, guild_id):
    data = await db.fetchrow("SELECT role FROM inventory WHERE user_id = $1 AND guild_id = $2", user_id, guild_id)
    