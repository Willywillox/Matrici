# Uso di Microsoft Access con più utenti e archiviazione su SharePoint

Questa nota sintetizza i limiti e le configurazioni consigliate se si vuole usare un database Microsoft Access in un contesto multi-utente, con il file `.accdb` salvato su SharePoint/OneDrive.

## Concorrenza e blocchi
- Access supporta l'accesso concorrente **solo** tramite un file condiviso su un file share che espone il protocollo SMB; in questo scenario crea un file `*.laccdb` per gestire i lock a livello di record.
- Su SharePoint/OneDrive il file viene sincronizzato a livello di **versioni** e non di blocchi record: le modifiche sono serializzate dal client di sync, con alto rischio di conflitti e corruzione se più utenti aprono/modificano il database contemporaneamente.
- Anche con l'opzione "blocco a livello di record" abilitata in Access, il locking non funziona correttamente su SharePoint perché il file non è aperto via SMB, ma tramite layer WebDAV/HTTP.

## Rischi principali
- **Corruzione del file**: se due client sincronizzano modifiche diverse, SharePoint crea copie in conflitto; Access può non riuscire a riaprire correttamente il database.
- **Prestazioni scarse**: ogni operazione comporta round-trip HTTP e sync locale; le query risultano lente e soggette a time-out.
- **Blocchi non affidabili**: i lock del file vengono gestiti dal sync client, non in tempo reale tra i processi Access.

## Raccomandazioni
- Evita di usare un file `.accdb` direttamente su SharePoint per accesso multi-utente simultaneo.
- Se si vuole rimanere su Access, usa una condivisione di rete SMB tradizionale (NAS/Fileserver) raggiungibile da tutti i client e abilita il locking a livello di record.
- Valuta un backend robusto (es. SQL Server Express, PostgreSQL o SQLite su server) con Access usato solo come front-end: la concorrenza viene gestita dal motore SQL, non da file sharing.
- Per scenari cloud con SharePoint/OneDrive, considera di spostare i dati su un database remoto e distribuire solo file front-end (`.accdb` collegato) aggiornati.

## Passi minimi se si resta con Access
1. **Non archiviare il file dati su SharePoint/OneDrive**: mettilo su una cartella di rete SMB con permessi adeguati.
2. **Abilita il blocco a livello di record** in Access (Opzioni > Avanzate) e verifica che il file `*.laccdb` venga creato quando un utente apre il DB.
3. **Backup frequenti**: Access non ha journaling; pianifica copie automatiche del file per ridurre il rischio di perdita dati.
4. **Test multi-utente**: prova in laboratorio con 2-3 client in parallelo per verificare tempi di risposta e assenza di conflitti.

## Sintesi
- SharePoint/OneDrive non è adatto come storage diretto per un database Access usato da più persone contemporaneamente.
- Usa un file share SMB o, meglio, migra i dati a un motore SQL e mantieni Access solo come interfaccia.
