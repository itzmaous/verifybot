import discord
from discord import app_commands
from discord.ext import commands
import os

TOKEN = os.getenv("token")
GUILD_ID = 1340669678951071825  # ID máy chủ Discord
CATEGORY_ID = 1340669682549657650  # ID danh mục chứa các ticket
ADMIN_ROLE_ID = 1345716116785336330  # Thay bằng ID role admin

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

tree = bot.tree  # Sử dụng bot.tree thay vì tạo CommandTree mới

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Mua Hàng", description="Liên hệ để mua hàng", emoji="🛒", value="mua-hang"),
            discord.SelectOption(label="Hỗ Trợ", description="Nhận hỗ trợ kỹ thuật", emoji="🛠️", value="ho-tro"),
        ]
        super().__init__(placeholder="Chọn loại ticket...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await self.view.create_ticket(interaction, self.values[0])

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str):
        guild = bot.get_guild(GUILD_ID)
        category = guild.get_channel(CATEGORY_ID)
        ticket_name = f"{ticket_type}-{interaction.user.name}"
        
        existing_channel = discord.utils.get(guild.channels, name=ticket_name)
        if existing_channel:
            await interaction.response.send_message(f"Bạn đã có một ticket mở: {existing_channel.mention}", ephemeral=True)
            return
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        ticket_channel = await guild.create_text_channel(ticket_name, category=category, overwrites=overwrites)
        embed = discord.Embed(title="🎟️ Ticket Mới", color=discord.Color.green())
        embed.add_field(name="Người tạo:", value=interaction.user.mention, inline=True)
        embed.add_field(name="Loại Ticket:", value=ticket_type, inline=True)
        embed.set_footer(text=f"ID: {interaction.user.id}")
        
        view = TicketActionView()
        admin_role = discord.utils.get(guild.roles, id=ADMIN_ROLE_ID)
        await ticket_channel.send(f"|| {admin_role.mention} {interaction.user.mention} ||", embed=embed, view=view)
        await interaction.response.send_message(f"Ticket của bạn đã được tạo: {ticket_channel.mention}", ephemeral=True)


class TicketActionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketButton("🔒 Close", "close", discord.ButtonStyle.danger))
        self.add_item(TicketButton("👤 Claim", "claim", discord.ButtonStyle.success))


class TicketButton(discord.ui.Button):
    def __init__(self, label, action, style):
        super().__init__(label=label, style=style)
        self.action = action

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        admin_role = discord.utils.get(guild.roles, id=ADMIN_ROLE_ID)
        
        if self.action == "close":
            if admin_role in interaction.user.roles:
                await interaction.channel.delete()
            else:
                await interaction.response.send_message("Chỉ admin mới có thể đóng ticket này!", ephemeral=True)
        elif self.action == "claim":
            await interaction.response.send_message(f"{interaction.user.mention} đã nhận xử lý ticket này!", ephemeral=False)

CHANNEL_ID = 1340669682843385896  # ID của kênh cố định

@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"Bot {bot.user} đã sẵn sàng!")

    # Gửi embed vào kênh cố định
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        async for message in channel.history(limit=10):  # Kiểm tra 10 tin nhắn gần nhất để tránh gửi trùng
            if message.author == bot.user and message.embeds:
                return  # Nếu đã có embed của bot, không gửi lại

        embed = discord.Embed(
            title="Maous Store | Ticket",
            description=(
                "Hãy chọn đúng option mà bạn cần để mở **ticket**\n\n"
                "### **🛒 : Chọn option này để mua sản phẩm!!**\n"
                "### **🛠️ : Chọn option này để yêu cầu hỗ trợ!!**"
            ),
            color=discord.Color.red()
        )

        # Thêm thumbnail và hình ảnh
        embed.set_thumbnail(url="https://img.upanh.tv/2025/04/05/88f30fd98515be8ccd42d0d289ee173ee0d53b2a28c604b904461477778149ae---Copy.png")
        embed.set_image(url="https://img.upanh.tv/2025/04/05/88f30fd98515be8ccd42d0d289ee173ee0d53b2a28c604b904461477778149ae.png")

        # Footer chuyên nghiệp hơn
        embed.set_footer(
            text="Maous Store • 2025",
            icon_url="https://img.upanh.tv/2025/04/05/88f30fd98515be8ccd42d0d289ee173ee0d53b2a28c604b904461477778149ae---Copy.png"
        )

        view = TicketView()
        await channel.send(embed=embed, view=view)  # Gửi vào kênh cố định


bot.run(TOKEN)
