from .nick_changer import NickChanger


async def setup(bot):
    await bot.add_cog(NickChanger())
