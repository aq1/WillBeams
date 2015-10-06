import utils
import parser
import qhandler
import downloader


def start_scraper(url, q_name, parsers, downloaders):
    task_q = qhandler.get_task_q()

    for sections in utils.chunk_list(utils.SECTIONS, parsers):
        webm_q = qhandler.create_channel(queue_name=q_name)
        parser.start_thread(task_q, webm_q, url, sections)

    for _ in range(downloaders):
        channel = qhandler.create_channel(queue_name=q_name)
        downloader.start_thread(channel, q_name)


def stop_scraper(parsers, downloaders):
    task_q = qhandler.get_task_q()

    for _ in range(parsers + downloaders):
        task_q.put(utils.STOP_SIGNAL)


if __name__ == '__main__':
    url = utils.BOARD_URL
    parsers = utils.PARSERS
    downloaders = utils.DOWNLOADERS
    q_name = utils.Q_NAME
    start_scraper(url, q_name, parsers=parsers, downloaders=downloaders)

    try:
        while True:
            pass

    except (KeyboardInterrupt, SystemExit):
        stop_scraper(parsers, downloaders)
