import dns.resolver

# Common disposable/temporary email providers. Not exhaustive - new ones
# appear constantly - but catches the well-known ones people actually use
# to dodge registration checks.
DISPOSABLE_DOMAINS = {
    "mailinator.com", "guerrillamail.com", "guerrillamail.info", "guerrillamail.biz",
    "guerrillamail.de", "guerrillamail.org", "sharklasers.com", "10minutemail.com",
    "10minutemail.net", "temp-mail.org", "temp-mail.io", "tempmail.com", "tempmail.net",
    "trashmail.com", "yopmail.com", "yopmail.fr", "yopmail.net", "throwawaymail.com",
    "fakeinbox.com", "getnada.com", "mailnesia.com", "mintemail.com", "spamgourmet.com",
    "dispostable.com", "maildrop.cc", "mohmal.com", "mailcatch.com", "emailondeck.com",
    "discard.email", "discardmail.com", "mytemp.email", "tempinbox.com", "burnermail.io",
    "mailsac.com", "inboxbear.com", "correotemporal.org", "tempmailo.com", "tempail.com",
    "0-mail.com", "1secmail.com", "1secmail.net", "1secmail.org", "airmail.cc",
    "anonbox.net", "byom.de", "dodgeit.com", "e4ward.com", "fakemailgenerator.com",
    "getairmail.com", "harakirimail.com", "incognitomail.org", "jetable.org",
    "mailexpire.com", "mailforspam.com", "mailismagic.com", "no-spam.ws", "pookmail.com",
    "sneakemail.com", "spam4.me", "spambog.com", "spamfree24.org", "spamgoes.in",
    "spaml.com", "spammotel.com", "spamobox.com", "trashdevil.com", "trashymail.com",
    "wegwerfmail.de", "wegwerfmail.net", "wegwerfmail.org", "zippymail.info",
}


def is_disposable_domain(domain):
    return domain.lower() in DISPOSABLE_DOMAINS


def has_mx_record(domain):
    """Best-effort DNS MX lookup. A confirmed 'this domain can't receive
    mail' answer fails validation; any resolver error (timeout, no network,
    misconfigured DNS) fails open rather than blocking real registrations
    over an infrastructure hiccup."""
    try:
        answers = dns.resolver.resolve(domain, "MX", lifetime=5)
        return len(answers) > 0
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        return False
    except Exception:
        return True
