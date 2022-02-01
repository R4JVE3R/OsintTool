import os
import platform
import re
import sys
from colorama import Fore, Style, init
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from time import monotonic
import requests
from requests_futures.sessions import FuturesSession
from torrequest import TorRequest
from result import QueryStatus
from result import QueryResult
from notify import QueryNotifyPrint
from sites  import SitesInformation

module_name = "Sherlock: Find Usernames Across Social Networks"
__version__ = "0.1"

class SherlockFuturesSession(FuturesSession):
    def request(self, method, url, hooks={}, *args, **kwargs):
        start = monotonic()

        def response_time(resp, *args, **kwargs):
            resp.elapsed = monotonic() - start

            return
        try:
            if isinstance(hooks['response'], list):
                hooks['response'].insert(0, response_time)
            elif isinstance(hooks['response'], tuple):
                hooks['response'] = list(hooks['response'])
                hooks['response'].insert(0, response_time)
            else:
                hooks['response'] = [response_time, hooks['response']]
        except KeyError:
            hooks['response'] = [response_time]
        return super(SherlockFuturesSession, self).request(method,
                                                           url,
                                                           hooks=hooks,
                                                           *args, **kwargs)


def get_response(request_future, error_type, social_network):

    response = None

    error_context = "General Unknown Error"
    expection_text = None
    try:
        response = request_future.result()
        if response.status_code:
            error_context = None
    except requests.exceptions.HTTPError as errh:
        error_context = "HTTP Error"
        expection_text = str(errh)
    except requests.exceptions.ProxyError as errp:
        error_context = "Proxy Error"
        expection_text = str(errp)
    except requests.exceptions.ConnectionError as errc:
        error_context = "Error Connecting"
        expection_text = str(errc)
    except requests.exceptions.Timeout as errt:
        error_context = "Timeout Error"
        expection_text = str(errt)
    except requests.exceptions.RequestException as err:
        error_context = "Unknown Error"
        expection_text = str(err)

    return response, error_context, expection_text


def sherlock(username, site_data, query_notify,
             tor=False, unique_tor=False,
             proxy=None, timeout=None):
    
    query_notify.start(username)

    underlying_session = requests.session()
    underlying_request = requests.Request()

    if len(site_data) >= 20:
        max_workers=20
    else:
        max_workers=len(site_data)

    session = SherlockFuturesSession(max_workers=max_workers,
                                     session=underlying_session)

    results_total = {}

    for social_network, net_info in site_data.items():

        results_site = {}
        results_site['url_main'] = net_info.get("urlMain")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
        }

        if "headers" in net_info:
            headers.update(net_info["headers"])

        url = net_info["url"].format(username)
        regex_check = net_info.get("regexCheck")
        if regex_check and re.search(regex_check, username) is None:
            results_site['status'] = QueryResult(username,
                                                 social_network,
                                                 url,
                                                 QueryStatus.ILLEGAL)
            results_site["url_user"] = ""
            results_site['http_status'] = ""
            results_site['response_text'] = ""
            query_notify.update(results_site['status'])
        else:
            results_site["url_user"] = url
            url_probe = net_info.get("urlProbe")
            if url_probe is None:
                url_probe = url
            else:
                url_probe = url_probe.format(username)

            if (net_info["errorType"] == 'status_code' and
                net_info.get("request_head_only", True) == True):
                request_method = session.head
            else:
                request_method = session.get

            if net_info["errorType"] == "response_url":
                allow_redirects = False
            else:
                allow_redirects = True

            if proxy is not None:
                proxies = {"http": proxy, "https": proxy}
                future = request_method(url=url_probe, headers=headers,
                                        proxies=proxies,
                                        allow_redirects=allow_redirects,
                                        timeout=timeout
                                        )
            else:
                future = request_method(url=url_probe, headers=headers,
                                        allow_redirects=allow_redirects,
                                        timeout=timeout
                                        )

            net_info["request_future"] = future

            if unique_tor:
                underlying_request.reset_identity()

        results_total[social_network] = results_site

    for social_network, net_info in site_data.items():
        results_site = results_total.get(social_network)
        url = results_site.get("url_user")
        status = results_site.get("status")
        if status is not None:
            continue

        error_type = net_info["errorType"]

        future = net_info["request_future"]
        r, error_text, expection_text = get_response(request_future=future,
                                                     error_type=error_type,
                                                     social_network=social_network)

        try:
            response_time = r.elapsed
        except AttributeError:
            response_time = None
        try:
            http_status = r.status_code
        except:
            http_status = "?"
        try:
            response_text = r.text.encode(r.encoding)
        except:
            response_text = ""

        if error_text is not None:
            result = QueryResult(username,
                                 social_network,
                                 url,
                                 QueryStatus.UNKNOWN,
                                 query_time=response_time,
                                 context=error_text)
        elif error_type == "message":
            error_flag = True
            errors=net_info.get("errorMsg")

            if isinstance(errors,str):
                if errors in r.text:
                    error_flag = False
            else:
                for error in errors:
                    if error in r.text:
                        error_flag = False
                        break
            if error_flag:
                result = QueryResult(username,
                                     social_network,
                                     url,
                                     QueryStatus.CLAIMED,
                                     query_time=response_time)
            else:
                result = QueryResult(username,
                                     social_network,
                                     url,
                                     QueryStatus.AVAILABLE,
                                     query_time=response_time)
        elif error_type == "status_code":
            if not r.status_code >= 300 or r.status_code < 200:
                result = QueryResult(username,
                                     social_network,
                                     url,
                                     QueryStatus.CLAIMED,
                                     query_time=response_time)
            else:
                result = QueryResult(username,
                                     social_network,
                                     url,
                                     QueryStatus.AVAILABLE,
                                     query_time=response_time)
        elif error_type == "response_url":
            if 200 <= r.status_code < 300:
                result = QueryResult(username,
                                     social_network,
                                     url,
                                     QueryStatus.CLAIMED,
                                     query_time=response_time)
            else:
                result = QueryResult(username,
                                     social_network,
                                     url,
                                     QueryStatus.AVAILABLE,
                                     query_time=response_time)
        else:
            raise ValueError(f"Unknown Error Type '{error_type}' for "
                             f"site '{social_network}'")

        query_notify.update(result)
        results_site['status'] = result

        results_site['http_status'] = http_status
        results_site['response_text'] = response_text

        # Add this site's results into final dictionary with all of the other results.
        results_total[social_network] = results_site

    # Notify caller that all queries are finished.
    query_notify.finish()

    return results_total


def timeout_check(value):
    from argparse import ArgumentTypeError

    try:
        timeout = float(value)
    except:
        raise ArgumentTypeError(f"Timeout '{value}' must be a number.")
    if timeout <= 0:
        raise ArgumentTypeError(f"Timeout '{value}' must be greater than 0.0s.")
    return timeout


def main():

    version_string = f"%(prog)s {__version__}\n" +  \
                     f"{requests.__description__}:  {requests.__version__}\n" + \
                     f"Python:  {platform.python_version()}"

    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                            description=f"{module_name} (Version {__version__})"
                            )
    parser.add_argument("--version",
                        action="version",  version=version_string,
                        help="Display version information and dependencies."
                        )
    parser.add_argument("--verbose", "-v", "-d", "--debug",
                        action="store_true",  dest="verbose", default=False,
                        help="Display extra debugging information and metrics."
                        )
    parser.add_argument("--folderoutput", "-fo", dest="folderoutput",
                        help="If using multiple usernames, the output of the results will be saved to this folder."
                        )
    parser.add_argument("--output", "-o", dest="output",
                        help="If using single username, the output of the result will be saved to this file."
                        )
    parser.add_argument("--tor", "-t",
                        action="store_true", dest="tor", default=False,
                        help="Make requests over Tor; increases runtime; requires Tor to be installed and in system path.")
    parser.add_argument("--unique-tor", "-u",
                        action="store_true", dest="unique_tor", default=False,
                        help="Make requests over Tor with new Tor circuit after each request; increases runtime; requires Tor to be installed and in system path.")
    parser.add_argument("--csv",
                        action="store_true",  dest="csv", default=False,
                        help="Create Comma-Separated Values (CSV) File."
                        )
    parser.add_argument("--site",
                        action="append", metavar='SITE_NAME',
                        dest="site_list", default=None,
                        help="Limit analysis to just the listed sites. Add multiple options to specify more than one site."
                        )
    parser.add_argument("--proxy", "-p", metavar='PROXY_URL',
                        action="store", dest="proxy", default=None,
                        help="Make requests over a proxy. e.g. socks5://127.0.0.1:1080"
                        )
    parser.add_argument("--json", "-j", metavar="JSON_FILE",
                        dest="json_file", default=None,
                        help="Load data from a JSON file or an online, valid, JSON file.")
    parser.add_argument("--timeout",
                        action="store", metavar='TIMEOUT',
                        dest="timeout", type=timeout_check, default=None,
                        help="Time (in seconds) to wait for response to requests. "
                             "Default timeout is infinity. "
                             "A longer timeout will be more likely to get results from slow sites. "
                             "On the other hand, this may cause a long delay to gather all results."
                       )
    parser.add_argument("--print-all",
                        action="store_true", dest="print_all",
                        help="Output sites where the username was not found."
                       )
    parser.add_argument("--print-found",
                        action="store_false", dest="print_all", default=False,
                        help="Output sites where the username was found."
                       )
    parser.add_argument("--no-color",
                        action="store_true", dest="no_color", default=False,
                        help="Don't color terminal output"
                        )
    parser.add_argument("username",
                        nargs='+', metavar='USERNAMES',
                        action="store",
                        help="One or more usernames to check with social networks."
                        )
    parser.add_argument("--browse", "-b",
                        action="store_true", dest="browse", default=False,
                        help="Browse to all results on default browser.")

    parser.add_argument("--local", "-l",
                        action="store_true", default=False,
                        help="Force the use of the local data.json file.")

    args = parser.parse_args()

    # Argument check
    # TODO regex check on args.proxy
    if args.tor and (args.proxy is not None):
        raise Exception("Tor and Proxy cannot be set at the same time.")

    # Make prompts
    if args.proxy is not None:
        print("Using the proxy: " + args.proxy)

    if args.tor or args.unique_tor:
        print("Using Tor to make requests")
        print("Warning: some websites might refuse connecting over Tor, so note that using this option might increase connection errors.")

    # Check if both output methods are entered as input.
    if args.output is not None and args.folderoutput is not None:
        print("You can only use one of the output methods.")
        sys.exit(1)

    # Check validity for single username output.
    if args.output is not None and len(args.username) != 1:
        print("You can only use --output with a single username")
        sys.exit(1)


    # Create object with all information about sites we are aware of.
    try:
        if args.local:
            sites = SitesInformation(os.path.join(os.path.dirname(__file__), 'resources/data.json'))
        else:
            sites = SitesInformation(args.json_file)
    except Exception as error:
        print(f"ERROR:  {error}")
        sys.exit(1)

    site_data_all = {}
    for site in sites:
        site_data_all[site.name] = site.information

    if args.site_list is None:
        site_data = site_data_all
    else:
        site_data = {}
        site_missing = []
        for site in args.site_list:
            counter = 0
            for existing_site in site_data_all:
                if site.lower() == existing_site.lower():
                    site_data[existing_site] = site_data_all[existing_site]
                    counter += 1
            if counter == 0:
                site_missing.append(f"'{site}'")

        if site_missing:
            print(f"Error: Desired sites not found: {', '.join(site_missing)}.")

        if not site_data:
            sys.exit(1)

    query_notify = QueryNotifyPrint(result=None,
                                    verbose=args.verbose,
                                    print_all=args.print_all,
                                    color=not args.no_color)

    for username in args.username:
        results = sherlock(username,
                           site_data,
                           query_notify,
                           tor=args.tor,
                           unique_tor=args.unique_tor,
                           proxy=args.proxy,
                           timeout=args.timeout)

        if args.output:
            result_file = args.output
        elif args.folderoutput:
            os.makedirs(args.folderoutput, exist_ok=True)
            result_file = os.path.join(args.folderoutput, f"{username}.txt")
        else:
            result_file = f"{username}.txt"
        exists_counter = 0
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}
        x = requests.get("https://instagram.com/"+username,headers=headers)
        if x.status_code == 200:
            print((Style.BRIGHT + Fore.GREEN + "[+] Instagram: "  +Style.RESET_ALL + "https://instagram.com/"+username))
            exists_counter = 1
        with open(result_file, "w", encoding="utf-8") as file:
            for website_name in results:
                dictionary = results[website_name]
                if dictionary.get("status").status == QueryStatus.CLAIMED:
                    exists_counter += 1
                    file.write(dictionary["url_user"] + "\n")
            file.write(f"Total Websites Username Detected On : {exists_counter}\n")
        print(f"\n[*] This username exist on total {exists_counter} websites.")

if __name__ == "__main__":
    main()
