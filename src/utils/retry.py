import time
import functools
from typing import Callable, Any, Tuple, Type


def retry_on_exception(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        print(f"エラーが発生しました（{attempt + 1}/{max_retries + 1}回目）: {str(e)}")
                        print(f"{current_delay}秒後にリトライします...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        print(f"最大リトライ回数に達しました。処理を中止します。")
            
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator