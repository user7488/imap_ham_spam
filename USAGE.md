


export IMAP_USER="you@gmail.com" IMAP_PASS="app-password"
python fetch_training_data.py   # fetch training emails
python train.py                 # train classifiers
python daemon.py     