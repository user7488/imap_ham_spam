**Yes, you can run the whole thing client-side**—no server admin rights needed.  
You keep the three Bayes brains on your own machine and let a small daemon sign in to the IMAP account, score each new INBOX message against the three models, and **MOVE** it to the right folder.

--------------------------------------------------------
What it looks like in practice
--------------------------------------------------------

1. **Train once**  
   - Drag a few hundred messages into local folders  
     `~/Mail/Train.BILLING`, `Train.NEWSLETTERS`, `Train.LOWIMPORTANCE`.  
   - A short Python script (`train.py`) feeds each folder into **three independent SpamBayes databases**:

   ```
   sb_filter.py --ham  Train.BILLING/*
   sb_filter.py --spam Train.BILLING/*      # teaches the BILLING classifier
   sb_filter.py --ham  Train.NEWSLETTERS/*  # teaches the NEWSLETTERS classifier
   …and so on
   ```

   The databases are stored as plain files (`~/.spambayes/billing.db`, `newsletters.db`, `lowimportance.db`)[^1][^3].

2. **Filtering daemon**  
   - Install **imapfilter** (a single C binary) or the Python helper **AI-IMAP-Spam-Filter**[^4][^6].  
   - A 30-line Lua (or Python) config logs in via IMAP-TLS, fetches only **unseen** messages, calls the three classifiers, and moves the mail:

   ```
   billing     = 0.90
   newsletters = 0.90
   lowimp      = 0.90

   for _,m in ipairs(INBOX:is_unseen()) do
       body = m:fetch_message()
       if bayes_score(body, 'billing') >= billing then
           m:move_messages(BILLING)
       elseif bayes_score(body, 'newsletters') >= newsletters then
           m:move_messages(NEWSLETTERS)
       elseif bayes_score(body, 'lowimportance') >= lowimp then
           m:move_messages(LOWIMPORTANCE)
       end
   end
   ```

   `bayes_score()` is just a wrapper that pipes the message to  
   `sb_filter.py --classify --database ~/.spambayes/billing.db` and returns the probability[^1].

3. **Keep learning**  
   - Whenever you drag a mis-filed message back into the correct folder, run the same `train.py` again; SpamBayes updates the relevant database instantly.

--------------------------------------------------------
Caveats
--------------------------------------------------------
- Your computer must be **online** and the daemon must be **running** for filtering to happen (same as any desktop mail rule)[^2][^5].  
- The first time you train you need ≈ 50–100 messages per class; after that it self-improves.  
- If you use **several clients** (phone, laptop) you’ll see the moves only after the daemon has processed the message—there’s no server-side magic.

--------------------------------------------------------
Bottom line
--------------------------------------------------------
With **SpamBayes** (or **bogofilter**, **crm114**, …) plus **imapfilter** you get **three independent Bayesian classifiers** that live entirely on your machine and still do server-side IMAP moves—no root, no SMTP hooks, no manual sieve rules.

[^1]: [Applications](https://spambayes.sourceforge.io/applications.html) (30%)
[^2]: [GitHub - andreasscherbaum/imap-mailfilter: IMAP Mailfilter](https://github.com/andreasscherbaum/imap-mailfilter) (22%)
[^3]: [SpamBayes: Bayesian anti-spam classifier written in Python.](https://spambayes.sourceforge.io/) (18%)
[^4]: [GitHub - lefcha/imapfilter: IMAP mail filtering utility](https://github.com/lefcha/imapfilter) (16%)
[^5]: [Bayesian SPAM Filtering - Mail](https://forum.emclient.com/t/bayesian-spam-filtering/36896) (8%)
[^6]: [GitHub - ekene-okafor/AI-IMAP-Spam-Filter](https://github.com/ekene-okafor/AI-IMAP-Spam-Filter) (6%)
