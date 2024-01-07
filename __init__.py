from os.path import join, dirname

from json_database import JsonStorage

from ovos_utils.ocp import MediaType, PlaybackType
from ovos_workshop.decorators.ocp import ocp_search, ocp_featured_media
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill


class SilentHallOfFameSkill(OVOSCommonPlaybackSkill):
    def __init__(self, *args, **kwargs):
        self.supported_media = [MediaType.SILENT_MOVIE]
        self.skill_icon = join(dirname(__file__), "ui", "silent_hof_icon.gif")
        self.archive = {v["streams"][0]: v for v in JsonStorage(f"{dirname(__file__)}/silenthalloffame.json").values()
                        if v["streams"]}
        super().__init__(*args, **kwargs)
        self.load_ocp_keywords()

    def load_ocp_keywords(self):
        movies = []
        directors = []
        actors = []

        for url, data in self.archive.items():
            t = data["title"].split("|")[0].split("(")[0].strip()

            if " starring " in data["title"]:
                actor = data["title"].split(" starring ")[-1]
                actor = actor.split("-")[0].split("(")[0].strip()
                if " and " in actor:
                    actor, actor2 = actor.split(" and ")
                    actors.append(actor2.strip())
                if "," in actor:
                    actor, actor2 = actor.split(",")
                    actors.append(actor2.strip())
                actors.append(actor.strip())
            if " featuring " in data["title"]:
                actor = data["title"].split(" featuring ")[-1]
                actor = actor.split("-")[0].split("(")[0].strip()
                if " and " in actor:
                    actor, actor2 = actor.split(" and ")
                    actors.append(actor2.strip())
                if "," in actor:
                    actor, actor2 = actor.split(",")
                    actors.append(actor2.strip())
                actors.append(actor.strip())

            if " director " in data["title"]:
                director = data["title"].split(" director ")[-1].split("(")[0].split(",")[0].split(" starring ")[0].split(" featuring ")[0].split(" with ")[0].split(" cinematographer ")[0]
                directors.append(director)

            if '"' in t:
                t = t.split('"')[1]
            else:
                t = t.split(",")[0].split(" 19")[0].split("/")[0].split("-")[0].split("[")[0].replace(
                    ".", " ")
            movies.append(t.strip())

        self.register_ocp_keyword(MediaType.SILENT_MOVIE,
                                  "silent_movie_name", movies)
        self.register_ocp_keyword(MediaType.MOVIE,
                                  "movie_director", directors)
        self.register_ocp_keyword(MediaType.MOVIE,
                                  "movie_actor", actors)
        self.register_ocp_keyword(MediaType.MOVIE,
                                  "movie_streaming_provider",
                                  ["SilentHallOfFame",
                                   "Silent Hall Of Fame"])

    def get_playlist(self, score=50, num_entries=25):
        pl = self.featured_media()[:num_entries]
        return {
            "match_confidence": score,
            "media_type": MediaType.MOVIE,
            "playlist": pl,
            "playback": PlaybackType.VIDEO,
            "skill_icon": self.skill_icon,
            "image": self.skill_icon,
            "title": "Silent Hall Of Fame (Movie Playlist)",
            "author": "Internet Archive"
        }

    @ocp_search()
    def search_db(self, phrase, media_type):
        base_score = 25 if media_type == MediaType.SILENT_MOVIE else 0
        entities = self.ocp_voc_match(phrase)

        title = entities.get("silent_movie_name")
        director = entities.get("movie_director")
        actor = entities.get("movie_actor")
        skill = "movie_streaming_provider" in entities  # skill matched

        base_score += 30 * len(entities)

        if title or director or actor:
            candidates = self.archive.values()

            if title:
                base_score += 30
                candidates = [video for video in self.archive.values()
                              if title.lower() in video["title"].lower()]
            elif actor:
                base_score += 35
                candidates = [video for video in self.archive.values()
                              if actor.lower() in video["title"].lower()]
            elif director:
                base_score += 35
                candidates = [video for video in self.archive.values()
                              if director.lower() in video["title"].lower()]

            for video in candidates:
                yield {
                    "title": video["title"],
                    "match_confidence": min(100, base_score),
                    "media_type": MediaType.BLACK_WHITE_MOVIE,
                    "uri": video["streams"][0],
                    "playback": PlaybackType.VIDEO,
                    "skill_icon": self.skill_icon,
                    "skill_id": self.skill_id,
                    "image": video["images"][0] if video["images"] else self.skill_icon
                }

        if skill:
            yield self.get_playlist()

    @ocp_featured_media()
    def featured_media(self):
        return [{
            "title": video["title"],
            "match_confidence": 70,
            "media_type": MediaType.MOVIE,
            "uri": video["streams"][0],
            "playback": PlaybackType.VIDEO,
            "skill_icon": self.skill_icon,
            "skill_id": self.skill_id
        } for video in self.archive.values()]


if __name__ == "__main__":
    from ovos_utils.messagebus import FakeBus

    s = SilentHallOfFameSkill(bus=FakeBus(), skill_id="t.fake")
    for r in s.search_db("play a movie with Lon Chaney", MediaType.SILENT_MOVIE):
        print(r)
        # {'title': '"The Big City" (1928) starring  Lon Chaney and Marceline Day - a trailer', 'match_confidence': 90, 'media_type': <MediaType.BLACK_WHITE_MOVIE: 20>, 'uri': 'https://archive.org/download/1928.TheBigCitytrailerTodBrowningLonChaneyMarcelineDay/Preview-The-big-city.ogv', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': '"The Wicked Darling" (1919) director Tod Browning featuring Lon Chaney', 'match_confidence': 90, 'media_type': <MediaType.BLACK_WHITE_MOVIE: 20>, 'uri': 'https://archive.org/download/MyMovie_20180126/My Movie.ogv', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': '"The Hunchback of Notre Dame" (1923) starring Lon Chaney and Patsy Ruth Miller', 'match_confidence': 90, 'media_type': <MediaType.BLACK_WHITE_MOVIE: 20>, 'uri': 'https://archive.org/download/TheHunchbackOfNotreDame1923_201312/The-Hunchback-of-Notre-Dame-v2.ogv', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': '"The Penalty" (1920) starring Lon Chaney', 'match_confidence': 90, 'media_type': <MediaType.BLACK_WHITE_MOVIE: 20>, 'uri': 'https://archive.org/download/ThePenalty_201312/The Penalty.ogv', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': '"The Phantom of the Opera" (1925) starring Lon Chaney', 'match_confidence': 90, 'media_type': <MediaType.BLACK_WHITE_MOVIE: 20>, 'uri': 'https://archive.org/download/ThePhantomOfTheOpera_201612/The Phantom of the Opera.ogv', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': '"Victory" (1919) featuring Lon Chaney', 'match_confidence': 90, 'media_type': <MediaType.BLACK_WHITE_MOVIE: 20>, 'uri': 'https://archive.org/download/VICTORY_201708/VICTORY.mp4', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': '"He Who Gets Slapped" (1924) starring Lon Chaney', 'match_confidence': 90, 'media_type': <MediaType.BLACK_WHITE_MOVIE: 20>, 'uri': 'https://archive.org/download/mymovie_20190920/My Movie.ogv', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://archive.org/download/mymovie_20190920/My Movie.png'}
