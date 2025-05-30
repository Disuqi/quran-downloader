import requests
from typing import List, Dict, Set, Optional
import enum

class QuranAudioAPI:
    DEFAULT_RECITER_ID = 118
    _all_reciters: List[Dict] = []
    _reciters_name_to_id: Dict[str, int] = {}

    @staticmethod
    async def initialize() -> None:
        # Fetch reciters from the API
        response = requests.get("https://mp3quran.net/api/v3/reciters", params={"language": "eng"})
        QuranAudioAPI._all_reciters = response.json()['reciters']
        QuranAudioAPI._reciters_name_to_id = {reciter['name']: int(reciter['id']) for reciter in QuranAudioAPI._all_reciters}

    @staticmethod
    def get_sorted_names() -> List[str]:
        return sorted(QuranAudioAPI._reciters_name_to_id.keys(), key=str.casefold)

    @staticmethod
    def get_reciter_id_by_name(name: str) -> Optional[int]:
        return QuranAudioAPI._reciters_name_to_id.get(name)

    @staticmethod
    def list_reciters() -> List[Dict]:
        return QuranAudioAPI._all_reciters

    @staticmethod
    def get_reciter(id: int) -> Optional[Dict]:
        return next((reciter for reciter in QuranAudioAPI._all_reciters if reciter['id'] == id), None)

    @staticmethod
    async def get_surah_audio(surah: int, reciter_id: int, moshaf_type: 'MoshafType' = 'MoshafType.REWAYAT_HAFS_A_N_ASSEM_MURATTAL', allow_other_moshaf: bool = True) -> str:
        # Fetch reciter by id
        response = requests.get("https://mp3quran.net/api/v3/reciters", params={"language": "eng", "reciter": reciter_id})
        reciter = response.json()['reciters'][0]

        link = ""
        # Search through the moshafs for the correct one
        for moshaf in reciter['moshaf'][::-1]:
            if moshaf['moshaf_type'] == moshaf_type:
                if surah in map(int, moshaf['surah_list'].split(',')):
                    link = f"{moshaf['server']}{str(surah).zfill(3)}.mp3"
                break

        if not link and allow_other_moshaf:
            for moshaf in reciter['moshaf'][::-1]:
                if surah in map(int, moshaf['surah_list'].split(',')):
                    link = f"{moshaf['server']}{str(surah).zfill(3)}.mp3"
                    break

        if link:
            return link
        else:
            raise Exception(f"No audio found for surah {surah} and reciter {reciter_id}")


class MoshafType(enum.Enum):
    REWAYAT_HAFS_A_N_ASSEM_MURATTAL = 11
    ALMUSS_HAF_AL_MOJAWWAD = 222
    ALMUSS_HAF_AL_MO_LIM = 213
    REWAYAT_WARSH_A_N_NAFI = 181
    REWAYAT_HAFS_A_N_ASSEM_4 = 14
    REWAYAT_WARSH_A_N_NAFI_TARIQ_ABI_BAKER = 101
    REWAYAT_ALDORAI_A_N_AL_KISAI = 121
    REWAYAT_ALBIZI_A_N_IBN_KATHEER = 111
    REWAYAT_QALON_A_N_NAFI = 51
    REWAYAT_ALDORI_A_N_ABI_AMR = 131
    REWAYAT_WARSH_A_N_NAFI_MURATTAL = 21
    IBN_THAKWAN_A_N_IBN_AMER = 161
    SHO_BAH_A_N_ASIM = 151
    IBN_JAMMAZ_A_N_ABI_JAFAR = 201
    HESHAM_A_N_ABI_AMER = 191
    REWAYAT_KHALAF_A_N_HAMZAH = 31
    REWAYAT_ASSOSI_A_N_ABI_AMR = 71
    REWAYAT_ALBIZI_A_N_IBN_KATHEER_MURATTAL = 41
    REWAYAT_QUNBOL_A_N_IBN_KATHEER = 61
    REWAYAT_ROWIS_RAWIH_A_N_YAKOOB = 91
    REWAYAT_QALON_A_N_NAFI_TARIQ_ABI_NASHIT = 81
