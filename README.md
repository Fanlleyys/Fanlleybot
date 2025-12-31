---
title: Personal Assistant Bot
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_file: app.py
pinned: false
---

# Personal Assistant Telegram Bot

Bot Telegram pribadi untuk mengelola keuangan dan catatan harian.

## Fitur

### Tabungan
- `/tabung <jumlah>` - Menabung uang
- `/ambil <jumlah>` - Ambil tabungan
- `/saldo` - Cek saldo dan history

### Pengeluaran
- `/keluar <jumlah> <keterangan>` - Catat pengeluaran
- `/laporan` - Laporan pengeluaran minggu ini
- `/laporan_bulan` - Laporan pengeluaran bulan ini

Tips: Bisa pakai `k` atau `rb` untuk ribuan (10k = 10.000), `jt` untuk jutaan

### Catatan
- `/note <judul> <isi>` - Simpan catatan/password
- `/notes` - Lihat daftar catatan
- `/lihat <judul>` - Lihat isi catatan
- `/hapus_note <judul>` - Hapus catatan

## Setup

Set the following secrets in Space settings:
- `BOT_TOKEN` - Token from @BotFather
- `OWNER_ID` - Your Telegram User ID
