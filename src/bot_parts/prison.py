import discord
from discord.ext.commands import Cog
from discord.utils import get
from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.cog_ext import cog_slash
from src.DatabaseCommunication import Database
from src.errors import DuplicateEntry


ICON_LINK = r"https://www.notion.so/image/https%3A%2F%2Fstatic.thenounproject.com%2Fpng%2F394344-200.png?table=block&id=f4e81391-aa89-4d2d-b74f-75dd5580d072&spaceId=06bdd9c6-b9a9-4b95-a45e-1905629fac2c&width=250&userId=ef09ee7a-849b-43af-a22f-d0c7e11e15db&cache=v2"


class Prison(Cog):
    def __init__(self, client):
        self.client = client
        self.db = Database()

    @Cog.listener()
    async def on_ready(self):
        print("Prison Extension loaded")

    
    async def _get_embed(self, mbed_type: str, content: str) -> discord.Embed:
        """A helper function that returns either a short success embed or a short error embed.

        Args:
            mbed_type (str): Whether the message should be a success or an error message.
            content (str): The content of the message.

        Returns:
            discord.Embed: The requested message.
        """
        if mbed_type == "success":
            mbed = discord.Embed(
                title=f"{content}",
                description="",
                colour=discord.Colour.green()
            )
            return mbed
        elif mbed_type == "error":
            mbed = discord.Embed(
                title=f"{content}",
                description="",
                colour=discord.Colour.red()
            )
            return mbed


    @cog_slash(
        name="arrest",
        description="Arrests a member",
        options=[
            create_option(
                name="member",
                description="Give the member you want to imprison",
                option_type=6,
                required=True
            ),
            create_option(
                name="reason",
                description="Give a reason why you want to arrest that person",
                option_type=3,
                required=False
            )
        ]
    )
    async def arrest(self, ctx: SlashContext, member: discord.Member, reason: str="None"):
        """If a member is mentioned a channel in the Prisons Category is created that only the arrested member and admins can join.
        The permissions the arrested member has is determined by the prisoner role that is necessary for the function to work.

        Args:
            ctx (SlashContext): Object passed to communicate with discord.
            member (discord.Member): The member that is going to be arrested.
            reason (str, optional): The reason that is going to be saved in the database. It shows up in the /checkprison message. Defaults to "None".
        """
        if not ctx.author.guild_permissions.kick_members:
            await ctx.send(embed=await self._get_embed("error", ":x: You have not the right to kick members"))
            return

        if member == self.client.user:
            await ctx.send(embed=await self._get_embed("error", ":x: You can't send me to prison I'm way to powerful!"))
            return

        if member == ctx.author:
            await ctx.send(embed=await self._get_embed("error", ":x: You can't send yourself to prison :face_with_raised_eyebrow:"))
            return

        imprisoned: bool = self.db.find_is_imprisoned(ctx.guild.id, member.id)
        if imprisoned:  # ERROR: Already in prisons
            await ctx.send(embed=await self._get_embed("error", ":x: this person is already imprisoned"))
            return

        if member.top_role >= ctx.author.top_role:  # ERROR: member higher than author
            await ctx.send(embed=await self._get_embed("error", ":x: The member has a higher or an euqal role"))
            return
        godbot_role: discord.Role = get(ctx.guild.roles, name="GodBot")
        if member.top_role >= godbot_role:  # ERROR: member higher than bot
            await ctx.send(embed=await self._get_embed("error", ":x: The member is too powerful to be arrested"))
            return

        prisoner_role = get(ctx.guild.roles, name="Prisoner")
        if prisoner_role is None:  # ERROR: No Prisoner Role
            await ctx.send(embed=await self._get_embed("error", ":x: There is no Prisoner role. Please create it first then try again"))
            return

        category = get(ctx.guild.categories, name="Prisons")
        if category is None:  # ERROR: No Category named Prisons
            await ctx.send(embed=await self._get_embed("error", ":x: There is no category named Prisons. Please create it first then try again"))
            return

        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(connect=False, manage_channels=False),
            ctx.guild.me: discord.PermissionOverwrite(manage_channels=True, connect=True),
            member: discord.PermissionOverwrite(connect=True)
        }

        prison_channel = await ctx.guild.create_voice_channel(f"{member.display_name}'s Cell", category=category,
                                                       overwrites=overwrites)

        roles_list = []
        for role in member.roles:
            if role.name == "@everyone":
                continue
            if role == ctx.guild.premium_subscriber_role:
                continue
            roles_list.append([role.id, role.name])
            await member.remove_roles(role)
        await member.add_roles(prisoner_role, atomic=True)

        voice_state = member.voice
        if voice_state is not None:
            await member.move_to(prison_channel)

        try:
            self.db.create_prison(ctx.guild.id, member.id, member.name, member.discriminator, prison_channel.id, roles_list, reason)
        except DuplicateEntry:
            await ctx.send(embed=await self._get_embed("error", "A duplicate entry appeared in the database please do not manually delete prisons. The member is still imprisoned"))

        await ctx.send(embed=await self._get_embed("success", f":white_check_mark: The member {member.mentoin} was arrested"))


    @cog_slash(
        name="release",
        description="Releases an imprisoned member",
        options=[
            create_option(
                name="member",
                description="Give the user you want to release",
                option_type=6,
                required=True
            )
        ]
    )
    async def release(self, ctx: SlashContext, member: discord.Member):
        """This function is the counterpart to arrest. Everything done in arrest will be reverted.
        The released member gets back all his roles taken from him in arrest.

        Args:
            ctx (SlashContext): Object passed to communicate with discord.
            member (discord.Member): The member that should be released.
        """
        if not ctx.author.guild_permissions.kick_members:
            await ctx.send(embed=await self._get_embed("error", ":x: You have not the right to kick members"))
            return

        is_imprisoned: bool = self.db.find_is_imprisoned(ctx.guild.id, member.id)
        if not is_imprisoned:
            await ctx.send(embed=await self._get_embed("error", f":x: {member.mention} is not imprisoned"))
            return

        prison_id: int = self.db.find_prison_id(ctx.guild.id, member.id)
        if prison_id == 0:
            await ctx.send(embed=await self._get_embed("error", ":x: I could not find the channelID from the prisoner chanenl. Please try again"))
            return

        prison = get(ctx.guild.channels, id=prison_id)  # get channel object
        if prison is None:
            await ctx.send(embed=await self._get_embed("error", "I could not find the prison channel. Dont't delete prison channels manually"))

        try:
            await prison.delete()
        except discord.NotFound:  # ERROR: Prison could not be deleted
            pass
        except discord.Forbidden as e:
            await ctx.send(embed=await self._get_embed("error", "Prison channel could not be deleted because I don't have permission to"))
        except discord.HTTPException:
            await ctx.send(embed=await self._get_embed("error", ":x: Could not delete the prison channel because discord didn't respond"))

        prisoner_role = get(ctx.guild.roles, name="Prisoner")
        await member.remove_roles(prisoner_role)
        roles: list = self.db.find_prisoner_roles(ctx.guild.id, member.id)
        if roles != []:
            for roles_list in roles:
                try:
                    await member.add_roles(get(ctx.guild.roles, id=roles_list[0]))
                except discord.Forbidden:
                    await ctx.send(embed=await self._get_embed("error", f":x: Ic ould not give the user {member.mention} the role {get(ctx.guild.roles, id=roles_list[0]).mention} because Id on't have permission"))
                except discord.HTTPException:
                    await ctx.send(embed=await self._get_embed("error", f":x: I could not give the user {member.mention} the role {get(ctx.guild.roles, id=roles_list[0]).mention}"))

        try:
            self.db.delete_prison(ctx.guild.id, member.id)
        except DuplicateEntry:
            await ctx.send(":x: A duplicate entry appeared. Please do not delete prisons manually.")
            await ctx.send(embed=await self._get_embed("error", "A duplicate entry appeared in the database please do not manually delete prisons"))

        await ctx.send(embed=await self._get_embed("success", f":white_check_mark: The member {member.mention} was released and all his roles are returned"))


    @cog_slash(
        name="checkprison",
        description="This shows you the imprisoned users and the reason"
    )
    async def checkprison(self, ctx):
        """Sends a nice embed that contains every imprisoned member with a date and a reason"""
        original_list: list = self.db.find_prisons(ctx.guild.id)
        if original_list == []:
            mbed = discord.Embed(
                title="Prison-list:",
                description="Empty",
                colour=0x979c9f
            )
            await ctx.send(embed=mbed)
            return
        mbed = discord.Embed(
            title="**Prison-list:**",
            description="{}".format("\n".join(original_list)),
            colour=0x979c9f
        )
        await ctx.send(embed=mbed)


def setup(client):
    client.add_cog(Prison(client))
