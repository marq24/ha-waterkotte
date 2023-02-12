""" Waterkotte Detection Module """
import aiohttp

ECOTOUCH = "ECOTOUCH"
EASYCON = "EASYCON"


async def waterkotte_detect(
    hostname: str, username: str, password: str
):  # pylint: disable=invalid-name, unused-argument
    """try to detect system"""
    try:
        async with aiohttp.ClientSession() as session:
            # r = await session.get("http://%s/cgi/login" % self.hostname, params=args)
            r = await session.get(
                f"http://{hostname}/http/easycon/cfg.wtk"
            )  # pylint: disable=invalid-name
            async with r:
                if r.status == 200:
                    print(r.text)
                    return EASYCON

                r = await session.get(f"http://{hostname}/cgi/login")
                async with r:
                    if r.status == 200:
                        return ECOTOUCH
    except:  # pylint: disable=bare-except
        pass
    return None
