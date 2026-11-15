import discord
from redbot.core import Config, commands


class NickChanger(commands.Cog):
    """Let people change the nicknames of members who opt in."""

    def __init__(self):
        self.config = Config.get_conf(self, identifier=2626487534, force_registration=True)
        self.config.register_guild(opted_in_users=[])

    async def get_opted_in_users(self, guild: discord.Guild) -> set[int]:
        return set(await self.config.guild(guild).opted_in_users())

    async def set_opted_in(self, member: discord.Member, opted_in: bool):
        async with self.config.guild(member.guild).opted_in_users() as saved_users:
            opted_in_users = set(saved_users)
            if opted_in:
                opted_in_users.add(member.id)
            else:
                opted_in_users.discard(member.id)
            saved_users[:] = sorted(opted_in_users)

    @commands.hybrid_group(name="nick")
    @commands.guild_only()
    async def nick(self, ctx: commands.Context):
        """Nickname commands for this server."""

    @nick.command(name="change")
    @commands.guild_only()
    async def change_nick(self, ctx: commands.Context, member: discord.Member, *, new_nick: str):
        """Change the nickname of an opted-in member."""
        opted_in_users = await self.get_opted_in_users(ctx.guild)
        if member.id not in opted_in_users:
            await ctx.send(
                f"{member.display_name} has not opted in to nickname changes.",
                ephemeral=bool(ctx.interaction),
            )
            return

        try:
            await member.edit(nick=new_nick)
        except discord.HTTPException:
            await ctx.send(
                "I couldn't change that nickname. Check my permissions and role position.",
                ephemeral=bool(ctx.interaction),
            )
            return

        await ctx.send(f"Changed {member.mention}'s nickname to {new_nick}.")

    @nick.command(name="opt_in")
    @commands.guild_only()
    async def opt_in(self, ctx: commands.Context):
        """Allow other members to change your nickname in this server."""
        await self.set_opted_in(ctx.author, True)
        await ctx.send(f"{ctx.author.display_name} has opted in to nickname changes.")

    @nick.command(name="opt_out")
    @commands.guild_only()
    async def opt_out(self, ctx: commands.Context):
        """Stop other members from changing your nickname in this server."""
        await self.set_opted_in(ctx.author, False)
        await ctx.send(f"{ctx.author.display_name} has opted out of nickname changes.")
