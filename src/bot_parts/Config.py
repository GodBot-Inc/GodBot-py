import discord
from discord.ext import commands
from discord.utils import get
from discord.ext.commands import Cog
from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from discord_slash.cog_ext import cog_slash
from utility.DatabaseCommunication import Database
from pprint import pprint


ICON_LINK = r"https://notion-emojis.s3-us-west-2.amazonaws.com/v0/svg-twitter/2699-fe0f.svg"


class Config(Cog):
	"""This is a part which is there to customize the godbot"""
	def __init__(self, client):
		self.client = client
		self.db = Database()

	@Cog.listener()
	async def on_ready(self):
		print("Config extension loaded")

	@cog_slash(
		name="setup",
		description="Sets up the bot so it works properly"
	)
	async def _setup(self, ctx: SlashContext):
		await ctx.send(":x: This command is in Development")
		godbot_role = get(ctx.guild.roles, name="GodBot")
		if godbot_role is None:
			await ctx.send(embed=discord.Embed(title=":x: COuld not get the GodBot role and change it's colour to `e2c766`", description="", colour=discord.Colour.red()))
		else:
			try:
				await godbot_role.edit(colour=0xe2c766, hoist=True, reason="Changed colour of GodBot role and made allowed it to be a group")
			except (discord.Forbidden, discord.HTTPException):
				pass
		prison = False
		private = False
		print(type(ctx.guild.categories))
		pprint(ctx.guild.categories)
		for category in ctx.guild.categories:
			if category.name == "Prisons":
				prison = True
			elif category.name == "Privaterooms":
				private = True
		if not prison:
			try:
				category = await ctx.guild.create_category("Prisons")
				await ctx.send(embed=discord.Embed(title=f":white_check_mark: Created category {category.mention}", description="", colour=discord.Colour.green()))
			except(discord.Forbidden, discord.HTTPException):
				await ctx.send(embed=discord.Embed(title=f":x: Could not create Prisons Category", description="", colour=discord.Colour.red()))
		if not private:
			try:
				category = await ctx.guild.create_category("Privaterooms")
				await ctx.send(embed=discord.Embed(title=f":white_check_mark: Created category {category.mention}", description="", colour=discord.Colour.green()))
			except (discord.Forbidden, discord.HTTPException):
				await ctx.send(embed=discord.Embed(title="Could not create Privaterooms category", description="", colour=discord.Colour.red()))


	@cog_slash(
        name="prereqs",
        description="Shows you everything the bot needs to work properly"
    )
	async def _prereqs(self, ctx: SlashContext):
		mbed = discord.Embed(
			title="Prerequirements",
			description="You can either do set all this things up manually or run `/setup`",
			colour=discord.Colour.light_grey()
		)
		mbed.add_field(name="**Prisons** Category", value="Under this category all prison channels will be created", inline=False)
		mbed.add_field(name="**Privaterooms** Category", value="Under this category all Privaterooms will be created. **NOTE:** As of now thisi not needed. Privaterooms will be introduced in next updates.", inline=False)
		mbed.add_field(name="**Prisoner** Role", value="Every member who's imprisoned will receive this role. With this you can modify the permissions prisoners have", inline=False)
		await ctx.send(embed=mbed)


def setup(client):
	client.add_cog(Config(client))
