import boto3
import logging
from signal_handler import CatchSignal
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

sqs = boto3.resource("sqs")    

def listen_queue(name: str, wait_time: int, max_batch_size: int) -> None:
    """
        :wait_time[int]: maximum time to wait before returning messages
        :max_batch_size[int]: maximum amount of returned messages per iteration
    """

    queue = sqs.get_queue_by_name(QueueName=name)
    signal_handler = CatchSignal()

    logger.info(f"Started consuming from queue: {name}")
    while not signal_handler.signal_issued:
        try:
            batch = queue.receive_messages(
                MessageAttributeNames=["All"],
                MaxNumberOfMessages=max_batch_size,
                WaitTimeSeconds=wait_time, # Long Polling
            )

            if len(batch):
                for m in batch:
                    # TODO call process
                    m.delete()
                logger.info(f"Batch Processed Count: {len(batch)}; Approximate queued messages: {queue.attributes["ApproximateNumberOfMessages"]}")
        except ClientError as error:
            logger.error(f"Failed to process message due to client error: {error}")

if __name__ == "__main__":
    listen_queue("secomp.fifo", 10, 1)