import telegram
from telegram.ext import CommandHandler, Updater
import paramiko
import config

MAX_MESSAGE_LENGTH = 4096

def start(update, context):
    update.message.reply_text("Bot telah diaktifkan!")

def run_script(update, context):
    chat_id = update.message.chat_id

    try:
        # Buat koneksi SSH
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(config.SSH_HOST, config.SSH_PORT, config.SSH_USERNAME, config.SSH_PASSWORD)

        # Kirim pesan awal
        update.message.reply_text("Proses sedang berjalan...")

        # Jalankan script pada VPS
        stdin, stdout, stderr = ssh_client.exec_command(f"bash {config.REMOTE_SCRIPT}")

        # Baca output dari script dan kirim sebagai pesan
        script_output = stdout.read().decode("utf-8")
        script_error = stderr.read().decode("utf-8")

        if script_error:
            update.message.reply_text(f"Terjadi kesalahan saat menjalankan script:\n{script_error}")
        else:
            update.message.reply_text(f"Output dari script:\n{script_output}")

        while script_output:
            update.message.reply_text(script_output[:MAX_MESSAGE_LENGTH])
            script_output = script_output[MAX_MESSAGE_LENGTH:]

        # Tutup koneksi SSH
        ssh_client.close()

        # Kirim pesan selesai
        update.message.reply_text("Proses selesai.")
    except Exception as e:
        update.message.reply_text(f"Terjadi kesalahan: {str(e)}")

def main():
    updater = Updater(token=config.BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    run_script_handler = CommandHandler('runscript', run_script)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(run_script_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()