#include "whisper_config.h"
#include "whisper_winapi.h"


int main() {
    printf("WhisperWinAPI standalone example");

    WhisperMessageBoxA(
        NULL,
        "SomeTitle",
        "SomeCaption",
        MB_CANCELTRYCONTINUE
    );
}