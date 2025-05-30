import sys
import os
import asyncio
import platform
import aiohttp
from loading_bar import LoadingBar
from quran_audio_api import QuranAudioAPI
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter, PathCompleter
from prompt_toolkit import PromptSession
from colored_print import print_debug, print_success, print_error, print_warning, print_info, print_subtitle, print_title
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, TRCK

# main.py
session = PromptSession()

suras_name_to_number = {
    "1": "Al-Fatiha",
    "2": "Al-Baqarah",
    "3": "Al-Imran",
    "4": "An-Nisa",
    "5": "Al-Ma'idah",
    "6": "Al-An'am",
    "7": "Al-A'raf",
    "8": "Al-Anfal",
    "9": "At-Tawbah",
    "10": "Yunus",
    "11": "Hud",
    "12": "Yusuf",
    "13": "Ar-Ra'd",
    "14": "Ibrahim",
    "15": "Al-Hijr",
    "16": "An-Nahl",
    "17": "Al-Isra",
    "18": "Al-Kahf",
    "19": "Maryam",
    "20": "Ta-Ha",
    "21": "Al-Anbiya",
    "22": "Al-Hajj",
    "23": "Al-Mu'minun",
    "24": "An-Nur",
    "25": "Al-Furqan",
    "26": "Ash-Shu'ara",
    "27": "An-Naml",
    "28": "Al-Qasas",
    "29": "Al-Ankabut",
    "30": "Ar-Rum",
    "31": "Luqman",
    "32": "As-Sajda",
    "33": "Al-Ahzab",
    "34": "Saba",
    "35": "Fatir",
    "36": "Ya-Sin",
    "37": "As-Saffat",
    "38": "Sad",
    "39": "Az-Zumar",
    "40": "Ghafir",
    "41": "Fussilat",
    "42": "Ash-Shura",
    "43": "Az-Zukhruf",
    "44": "Ad-Dukhan",
    "45": "Al-Jathiyah",
    "46": "Al-Ahqaf",
    "47": "Muhammad",
    "48": "Al-Fath",
    "49": "Al-Hujurat",
    "50": "Qaf",
    "51": "Adh-Dhariyat",
    "52": "At-Tur",
    "53": "An-Najm",
    "54": "Al-Qamar",
    "55": "Ar-Rahman",
    "56": "Al-Waqi'ah",
    "57": "Al-Hadid",
    "58": "Al-Mujadila",
    "59": "Al-Hashr",
    "60": "Al-Mumtahanah",
    "61": "As-Saff",
    "62": "Al-Jumu'ah",
    "63": "Al-Munafiqun",
    "64": "At-Taghabun",
    "65": "At-Talaq",
    "66": "At-Tahrim",
    "67": "Al-Mulk",
    "68": "Al-Qalam",
    "69": "Al-Haqqah",
    "70": "Al-Ma'arij",
    "71": "Nuh",
    "72": "Al-Jinn",
    "73": "Al-Muzzammil",
    "74": "Al-Muddaththir",
    "75": "Al-Qiyamah",
    "76": "Al-Insan",
    "77": "Al-Mursalat",
    "78": "An-Naba",
    "79": "An-Nazi'at",
    "80": "'Abasa",
    "81": "At-Takwir",
    "82": "Al-Infitar",
    "83": "Al-Mutaffifin",
    "84": "Al-Inshiqaq",
    "85": "Al-Buruj",
    "86": "At-Tariq",
    "87": "Al-A'la",
    "88": "Al-Ghashiyah",
    "89": "Al-Fajr",
    "90": "Al-Balad",
    "91": "Ash-Shams",
    "92": "Al-Lail",
    "93": "Ad-Duhaa",
    "94": "Ash-Sharh",
    "95": "At-Tin",
    "96": "Al-'Alaq",
    "97": "Al-Qadr",
    "98": "Al-Bayyinah",
    "99": "Az-Zalzalah",
    "100": "Al-Adiyat",
    "101": "Al-Qari'ah",
    "102": "At-Takathur",
    "103": "Al-Asr",
    "104": "Al-Humazah",
    "105": "Al-Fil",
    "106": "Quraysh",
    "107": "Al-Ma'un",
    "108": "Al-Kawthar",
    "109": "Al-Kafirun",
    "110": "An-Nasr",
    "111": "Al-Masad",
    "112": "Al-Ikhlas",
    "113": "Al-Falaq",
    "114": "An-Nas"
  }
suras_number_to_name = dict(map(reversed, suras_name_to_number.items()))

system = platform.system()
if system == 'Windows':
    download_location = os.path.expanduser('~\\Downloads')
else:
    download_location = os.path.expanduser('~/Downloads')

async def ask_for_surah():
    suras_list = [item for pair in suras_name_to_number.items() for item in pair]
 
    surah_completed = WordCompleter(suras_list, ignore_case=True)
    surah = await session.prompt_async("Enter the surah name of number: ", completer=surah_completed)
    surah = surah.strip()

    if surah is None or not surah:
        return None
    
    if suras_name_to_number.get(surah):
        surah = suras_name_to_number[surah]
    elif surah.isdigit() and surah in suras_number_to_name:
        surah = int(surah)
    else:
        return None

    return surah

async def ask_for_reciter():
    reciters = QuranAudioAPI.list_reciters()
    reciter_names = [reciter['name'] for reciter in reciters]
    reciter_completer = WordCompleter(reciter_names, ignore_case=True)

    reciter = await session.prompt_async("Enter the reciter name: ", completer=reciter_completer)
    reciter = QuranAudioAPI.get_reciter_id_by_name(reciter)

    return reciter

async def download_one_surah():
    surah = await ask_for_surah()
    if not surah:
        print_error("Invalid surah. Please try again.")
        return

    reciter = await ask_for_reciter()
    if not reciter:
        print_error("Given Reciter name does not exist. Please try again.")
        return

    await download_surah(surah, reciter)

async def download_all_surahs():
    reciter = await ask_for_reciter()
    if not reciter:
        print_error("Given Reciter name does not exist. Please try again.")
        return
    
    surahs = list(suras_number_to_name.keys())
    failed_surahs = await download_surahs(surahs, reciter)
    while failed_surahs:
        retry = await session.prompt_async(f"The following surahs have failed to download.\n[{', '.join(str(s) for s in failed_surahs)}]\n Do you want to retry? (yes/no): ", completer=None)
        if retry.lower() not in ['yes', 'y']:
            print_warning("Exiting download of failed surahs.")
            break
        print_info("Retrying failed surahs...")
        failed_surahs = await download_surahs(failed_surahs, reciter)

    print_success("Download Complete!")

async def download_surahs(surahs, reciter_id):
    loadingBar = LoadingBar("Downloading surahs", total=len(surahs))
    loadingBar.start()

    failed_surahs = []
    
    # Limit concurrent downloads to prevent overwhelming the server
    semaphore = asyncio.Semaphore(5)  # Only 5 downloads at once
    
    async def download_with_semaphore(surah):
        async with semaphore:
            success = False
            
            def onSuccess():
                nonlocal success
                success = True
                loadingBar.update()
            
            def onFail(failed_surah):
                nonlocal success
                success = False
                loadingBar.update()
                failed_surahs.append(failed_surah)
            
            await download_surah(str(surah), reciter_id, onSuccess=onSuccess, onFail=onFail)

    try:
        tasks = []
        for surah in surahs:
            tasks.append(download_with_semaphore(surah))

        await asyncio.gather(*tasks, return_exceptions=True)

        loadingBar.stop()
        return failed_surahs
    except Exception as e:
        loadingBar.stop()
        print_error(f"Download batch failed: {e}")
        return surahs  # Return all as failed

def list_reciters():
    print_subtitle("Reciters List:")
    reciters = QuranAudioAPI.get_sorted_names()
    for i, reciter in enumerate(reciters, start=1):
        print_info(f"{i}. {reciter}")

async def download_surah(surah, reciter_id, onSuccess=None, onFail=None, max_retries=3):
    for attempt in range(max_retries):
        try:
            reciter_name = QuranAudioAPI.get_reciter(int(reciter_id))['name']
            surah_name = suras_number_to_name[str(surah)]
            filepath = os.path.join(download_location, reciter_name, f"{surah_name}.mp3")
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            audio_link = await QuranAudioAPI.get_surah_audio(int(surah), reciter_id)

            # Configure connection with better timeouts
            timeout = aiohttp.ClientTimeout(total=300, connect=30, sock_read=30)
            connector = aiohttp.TCPConnector(
                limit=10,  # Limit concurrent connections
                limit_per_host=5,  # Limit per host
                ttl_dns_cache=300,
                use_dns_cache=True
            )

            async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
                async with session.get(audio_link) as response:
                    if response.status == 200:
                        await write_surah_to_file(filepath, response)
                        set_metadata(filepath, surah, surah_name, reciter_name)
                        if onSuccess:
                            onSuccess()
                        return  # Success, exit retry loop
                    else:
                        if attempt == max_retries - 1:  # Last attempt
                            if onFail:
                                onFail(surah)
                        else:
                            print_warning(f"Attempt {attempt + 1} failed for surah {surah}, retrying...")
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff

        except (aiohttp.ClientConnectionError, asyncio.TimeoutError, ssl.SSLError) as e:
            if attempt == max_retries - 1:  # Last attempt
                print_error(f"Failed to download surah {surah} after {max_retries} attempts: {e}")
                if onFail:
                    onFail(surah)
            else:
                print_warning(f"Attempt {attempt + 1} failed for surah {surah}: {e}, retrying...")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            print_error(f"Unexpected error downloading surah {surah}: {e}")
            if onFail:
                onFail(surah)
            break

async def write_surah_to_file(filepath, response):
    with open(filepath, 'wb') as file:
        async for chunk in response.content.iter_chunked(1024):
            file.write(chunk)

def set_metadata(filepath, surah_number, surah_name, reciter_name):
    audio = MP3(filepath, ID3=ID3)
        
    # Add ID3 tag if it doesn't exist
    if audio.tags is None:
        audio.add_tags()
    
    # Set metadata
    audio.tags.add(TIT2(encoding=3, text=surah_name))  # Title
    audio.tags.add(TPE1(encoding=3, text=reciter_name))  # Artist
    audio.tags.add(TALB(encoding=3, text=reciter_name))  # Album
    audio.tags.add(TCON(encoding=3, text="Quran"))  # Genre
    audio.tags.add(TRCK(encoding=3, text=f"{surah_number}/114"))  # Track number (current/total)
    
    # Save the changes
    audio.save()

async def set_download_location():
    completer = PathCompleter(only_directories=True, expanduser=True)
    new_location = await session.prompt_async("Enter the new download location: ", completer=completer)
    new_location = os.path.expanduser(new_location.strip())
    if not new_location:
        print_error("Invalid path. Please try again.")
        return

    os.makedirs(new_location, exist_ok=True)

    global download_location
    download_location = new_location
    print_debug(f"Download location set to: {download_location}")

def exit_app():
    print_warning("\nExiting the application...")
    print_debug("As-Salam Alaikom Wa Rahmatullahi Wa Barakatu!")
    sys.exit()

def show_menu():
    print_subtitle("\nMenu:")
    print_info("1 - Download one surah")
    print_info("2 - Download all surahs")
    print_info("3 - List reciters")
    print_info("4 - Set download location")
    print_info("5 - Show current download path")
    print_info("6 - Exit")

async def main():
    await QuranAudioAPI.initialize()
    os.makedirs(download_location, exist_ok=True)
    print_title("-- Quran Audio Downloader --")
    while True:
        show_menu()
        choice = await session.prompt_async("\nChoose an option (1-6): ")

        if choice == '1':
            await download_one_surah()
        elif choice == '2':
            await download_all_surahs()
        elif choice == '3':
            list_reciters()
        elif choice == '4':
            await set_download_location()
        elif choice == '5':
            print_debug(f"Current download path: {download_location}")
        elif choice == '6':
            exit_app()
        else:
            print_error("Invalid choice, please try again.")

if __name__ == "__main__":
    asyncio.run(main())
