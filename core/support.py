#!/usr/bin/env python3

## RewriteEngine rewrite rules and conditions
REWRITE = {
    'COND_IP':    '\tRewriteCond\t\t\t\texpr\t\t\t\t\t"-R \'{IP}\'"\t[OR]\n',
    'COND_HOST':  '\tRewriteCond\t\t\t\t%{{HTTP_HOST}}\t\t\t\t\t{HOSTNAME}\t[OR,NC]\n',
    'COND_AGENT': '\tRewriteCond\t\t\t\t%{{HTTP_USER_AGENT}}\t\t\t\t\t{AGENT}\t[OR,NC]\n',
    'END_COND':   '\tRewriteCond\t\t\t\texpr\t\t\t\t\t"-R \'192.168.250.250\'"\n',
    ## Removed Request Scheme so we can force the protocol we want to use for our redirection
    'RULE':       '\tRewriteRule\t\t\t\t^.*$\t\t\t\t\t${REDIR_TARGET}\t[L,R=302]\n'
}

def print_exclude_list():
    print('[+] Exclusion List:')
    print('    --------------')

    print('\n\tThis list represents the value(s) a user can pass to the `--exclude` argument in order')
    print('\tto exclude a specific data source from being added to the final redirect.rules file.')
    print('\tNOTE: The `--exclude` argument accepts keywords and/or specific IP/Host/User-Agent\'s')
    print('\tto be excluded delimited by: SPACE')

    print('\n\tExample usage of the `--exclude` argument:')
    print('\t\t--exclude user-agents radb 35.0.0.0/8')

    print('\n\tExclusion Keyword List:')
    print('\t----------------------')
    print('\t\tdynamic\t\t# Exclude all dynamic sources')
    print('\t\tstatic\t\t# Exclude all static sources')
    print('\t\thtaccess\t# Exclude @curi0usJack\'s .htaccess file')
    print('\t\tuser-agents\t# Exclude User-Agents file')
    print('\t\tips\t\t# Exclude IPs obtained via Malware Kit\'s and other sources')
    print('\t\thostnames\t# Exclude Hostnames obtained via Malware Kit\'s and other sources')
    print('\t\tasn\t\t# Exclude all ASN data')
    print('\t\tradb\t\t# Exclude ASN data from RADB')
    print('\t\tbgpview\t\t# Exclude ASN data from BGPView')
    print('\t\tAS#\t\t# Exclude a specific ASN based on AS# format')
    print('\t\tmisc\t\t# Exclude Misc data sources')
    print('\t\ttor\t\t# Exclude TOR Exit Node data')
    print('\t\tamazon\t\t# Exclude all Amazon data')
    print('\t\taws\t\t# Exclude AWS data')
    print('\t\tgoogle\t\t# Exclude all Google data')
    print('\t\tgooglecloud\t# Exclude Google Cloud data')
    print('\t\tmicrosoft\t# Exclude all Microsoft data')
    print('\t\tazure\t\t# Exclude MS Azure data')
    print('\t\toffice365\t# Exclude Office365 data')
    print('\t\toracle\t\t# Exclude all Oracle data')
    print('\t\toraclecloud\t# Exclude Oracle Cloud data')

    print('\n\tNOTE: Company names/identifiers used within the core/data/asns.py')
    print('\tfile can also be used.')
    print('\tExclude All ZScaler ASN\'s: `--exclude ZSCALER`')
    print('\tExclude ZScaler\'s ATL ASN: `--exclude ZSCALER-ATLANTA`')