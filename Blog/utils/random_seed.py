from datetime import datetime
import hashlib

def get_daily_seed(purpose="default", run_number=0, run_lvl=0, additional=None):
    """
    Returns a consistent random seed based on the current date and a specific purpose.
    
    Args:
        purpose: String identifier for what this randomness is used for
        run_number: Optional integer to differentiate between runs
        run_lvl: Optional integer to differentiate between levels
        additional: Optional string for any additional differentiation
        
    Returns:
        An integer seed value
    """
    today = datetime.now().strftime("%Y%m%d")  # Format: YYYYMMDD
    
    # Create a seed string combining date and purpose
    seed_string = f"{today}_{purpose}_{run_number}_{run_lvl}"
    if additional:
        seed_string += f"_{str(additional)}"
    # Ensure the seed string is unique and consistent
        
    # Use hash to convert string to integer
    hash_obj = hashlib.md5(seed_string.encode())
    # Convert first 8 bytes of hash to integer
    seed = int(hash_obj.hexdigest()[:8], 16)
    return seed