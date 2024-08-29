import random


def print_banner():
    """Prints a banner"""

    banner = rf"""{generate_random_color_escape()}
 __      __.__    .__                             _______          __            ________   _____  _____                    .__              
/  \    /  \  |__ |__| ____________   ___________ \      \   _____/  |_          \_____  \_/ ____\/ ____\____   ____   _____|__|__  __ ____  
\   \/\/   /  |  \|  |/  ___/\____ \_/ __ \_  __ \/   |   \_/ __ \   __\  ______  /   |   \   __\\   __\/ __ \ /    \ /  ___/  \  \/ // __ \ 
 \        /|   Y  \  |\___ \ |  |_> >  ___/|  | \/    |    \  ___/|  |   /_____/ /    |    \  |   |  | \  ___/|   |  \\___ \|  |\   /\  ___/ 
  \__/\  / |___|  /__/____  >|   __/ \___  >__|  \____|__  /\___  >__|           \_______  /__|   |__|  \___  >___|  /____  >__| \_/  \___  >
       \/       \/        \/ |__|        \/              \/     \/                       \/                 \/     \/     \/              \/ """
    print(banner)
    print("\033[0m")


def generate_random_color_escape():
    # List of some common color escape sequences
    color_sequences = [
        "\033[31m",  # Red
        "\033[32m",  # Green
        "\033[33m",  # Yellow
        "\033[34m",  # Blue
        "\033[35m",  # Magenta
        "\033[36m",  # Cyan
        "\033[37m",  # White
        "\033[90m",  # Bright Black (Gray)
        "\033[91m",  # Bright Red
        "\033[92m",  # Bright Green
        "\033[93m",  # Bright Yellow
        "\033[94m",  # Bright Blue
        "\033[95m",  # Bright Magenta
        "\033[96m",  # Bright Cyan
        "\033[97m",  # Bright White
    ]

    # Choose a random color escape sequence
    return random.choice(color_sequences)


if __name__ == "__main__":
    print_banner()
