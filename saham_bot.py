import requests
import pandas as pd
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime

TOKE=="8727250219:AAEAgdG8RhxzY4KmBDpLOlawpBlh6e5ZeEA"

def get_foreign_data():
    url = "https://www.idx.co.id/id/data-pasar/ringkasan-perdagangan/transaksi-asing/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find("table")
        if not table:
            return None
        rows = table.find_all("tr")
        data = []
        for row in rows[1:]:
            cols = row.find_all("td")
            if len(cols) >= 4:
                saham = cols[0].text.strip()
                net = cols[3].text.strip().replace(",", "").replace(".", "")
                try:
                    data.append({"kode": saham, "net_asing": int(net)})
                except:
                    pass
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "SahamIndo Bot\n\n"
        "/topbuy - Top net buy asing\n"
        "/topsell - Top net sell asing\n"
        "/cek KODE - Cek 1 saham\n"
        "/summary - Ringkasan asing"
    )

async def topbuy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Mengambil data...")
    df = get_foreign_data()
    if df is None or df.empty:
        await update.message.reply_text("Data tidak tersedia.")
        return
    df_sorted = df.sort_values("net_asing", ascending=False).head(10)
    msg = f"TOP NET BUY ASING\n{datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    for _, row in df_sorted.iterrows():
        msg += f"{row['kode']} -> {row['net_asing']:,} lot\n"
    await update.message.reply_text(msg)

async def topsell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Mengambil data...")
    df = get_foreign_data()
    if df is None or df.empty:
        await update.message.reply_text("Data tidak tersedia.")
        return
    df_sorted = df.sort_values("net_asing").head(10)
    msg = f"TOP NET SELL ASING\n{datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    for _, row in df_sorted.iterrows():
        msg += f"{row['kode']} -> {row['net_asing']:,} lot\n"
    await update.message.reply_text(msg)

async def cek_saham(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Contoh: /cek BBCA")
        return
    kode = context.args[0].upper()
    df = get_foreign_data()
    if df is None or df.empty:
        await update.message.reply_text("Data tidak tersedia.")
        return
    hasil = df[df["kode"] == kode]
    if hasil.empty:
        await update.message.reply_text(f"{kode} tidak ditemukan.")
        return
    row = hasil.iloc[0]
    net = row["net_asing"]
    status = "NET BUY" if net > 0 else "NET SELL"
    await update.message.reply_text(f"{kode}\nStatus: {status}\nNet: {net:,} lot")

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    df = get_foreign_data()
    if df is None or df.empty:
        await update.message.reply_text("Data tidak tersedia.")
        return
    total_buy = df[df["net_asing"] > 0]["net_asing"].sum()
    total_sell = df[df["net_asing"] < 0]["net_asing"].sum()
    net_total = total_buy + total_sell
    sentiment = "AKUMULASI" if net_total > 0 else "DISTRIBUSI"
    await update.message.reply_text(
        f"RINGKASAN ASING\n{datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
        f"Net Buy  : {total_buy:,}\n"
        f"Net Sell : {total_sell:,}\n"
        f"Total    : {net_total:,}\n"
        f"Sentimen : {sentiment}"
    )

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("topbuy", topbuy))
    app.add_handler(CommandHandler("topsell", topsell))
    app.add_handler(CommandHandler("cek", cek_saham))
    app.add_handler(CommandHandler("summary", summary))
    print("Bot aktif!")
    app.run_polling()

if __name__ == "__main__":
    main()
