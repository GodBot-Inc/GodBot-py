# Import every command validation script from jukebox
from time import sleep
from jukebox import (current_validation,
                     leave_validation,
                     loop_validation,
                     loopqueue_validation,
                     pause_validation,
                     play_validation,
                     play_random_validation,
                     queue_validation,
                     remove_validation,
                     removedupes_validation,
                     resume_validation,
                     search_validation,
                     skip_validation,
                     skipto_validation,
                     stop_validation,
                     volume_validation)


current_validation.authorize()
leave_validation.authorize()
loop_validation.authorize()
loopqueue_validation.authorize()
pause_validation.authorize()
sleep(21)
play_validation.authorize()
play_random_validation.authorize()
queue_validation.authorize()
remove_validation.authorize()
removedupes_validation.authorize()
sleep(21)
resume_validation.authorize()
search_validation.authorize()
skipto_validation.authorize()
skip_validation.authorize()
stop_validation.authorize()
sleep(21)
volume_validation.authorize()
