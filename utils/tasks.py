from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler(max_workers=30)
scheduler.start()
