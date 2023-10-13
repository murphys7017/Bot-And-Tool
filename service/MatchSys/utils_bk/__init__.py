from .doc_vec_tool import Doc2VecTool
from .filters import get_recent_repeated_responses
from .snowkey import IdWorker


def print_progress_bar(description, iteration_counter, total_items, progress_bar_length=20):
    """
    Print progress bar
    :param description: Training description
    :type description: str

    :param iteration_counter: Incremental counter
    :type iteration_counter: int

    :param total_items: total number items
    :type total_items: int

    :param progress_bar_length: Progress bar length
    :type progress_bar_length: int

    :returns: void
    :rtype: void
    """
    import sys

    percent = float(iteration_counter) / total_items
    hashes = '#' * int(round(percent * progress_bar_length))
    spaces = ' ' * (progress_bar_length - len(hashes))
    sys.stdout.write('\r{0}: [{1}] {2}%'.format(description, hashes + spaces, int(round(percent * 100))))
    sys.stdout.flush()
    if total_items == iteration_counter:
        print('\r')

__all__ = (
    'IdWorker',
    'Doc2VecTool',
    'print_progress_bar',
    'get_recent_repeated_responses'
)