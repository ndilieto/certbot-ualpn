"""TLS-ALPN-01 Authenticator for ualpn."""
import logging
import hashlib
import socket
import josepy as jose

import zope.interface

from acme import challenges
#from certbot import achallenges  # pylint: disable=unused-import
from certbot import errors
from certbot import interfaces
from certbot import reverter
from certbot.plugins import common

logger = logging.getLogger(__name__)

@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(common.Plugin):
    """TLS-ALPN-01 ualpn authenticator

    This authenticator sets up ualpn to fulfill a tls-alpn-01 challenge.
    See https://github.com/ndilieto/uacme#tls-alpn-01-challenge-support
    """

    description = 'Obtain certs with a tls-alpn-01 challenge using ualpn.'

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)

        self.reverter = reverter.Reverter(self.config)
        self.reverter.recovery_routine()

    @classmethod
    def add_parser_arguments(cls, add):  # pylint: disable=arguments-differ
        add('socket-path', help='Path to ualpn UNIX-domain socket',
            default='/run/ualpn.sock')

    def more_info(self):  # pylint: disable=missing-function-docstring
        return 'This plugin configures ualpn to respond to a tls-alpn-01 challenge.'

    def prepare(self):  # pylint: disable=missing-function-docstring
        pass

    def get_chall_pref(self, domain):
        # pylint: disable=unused-argument,missing-function-docstring
        return [challenges.TLSALPN01]

    def perform(self, achalls):  # pylint: disable=missing-function-docstring
        socket_path = self.conf('socket-path')
        if not socket_path:
            socket_path = '/run/ualpn.sock'

        responses = []
        for achall in achalls:
            kwargs = {}
            kwargs["cert_key"] = None
            kwargs["domain"] = achall.domain
            validation = achall.validation(achall.account_key, **kwargs)
            message = "auth {0} {1}\n".format(achall.domain,
                    jose.b64encode(hashlib.sha256(achall.key_authorization(
                        achall.account_key).encode("utf-8")).digest()).decode())
            try:
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.connect(socket_path)
                sock.sendall(message.encode())
                response = sock.recv(1024).decode().lstrip().rstrip()
                sock.close()
            except OSError as e:
                logger.debug('error talking to ualpn on %s: %s', socket_path, str(e))
                raise errors.PluginError('Error talking to ualpn on {0}: {1}'.format(
                    socket_path, str(e))) from None
                
            if response.startswith('OK'):
                logger.debug('ualpn: added %s', message)
            else:
                logger.debug('ualpn: error adding %s: %s', message, response)
                raise errors.PluginError('Error adding auth for {0} to ualpn: {1}'.format(
                    achall.domain, response)) from None
            responses.append(achall.response(achall.account_key))
        return responses

    def cleanup(self, achalls):  # pylint: disable=missing-function-docstring
        socket_path = self.conf('socket-path')
        if not socket_path:
            socket_path = '/run/ualpn.sock'

        for achall in achalls:
            message = "unauth {0}\n".format(achall.domain)
            try:
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.connect(socket_path)
                sock.sendall(message.encode())
                response = sock.recv(1024).decode().lstrip().rstrip()
                sock.close()
            except OSError as e:
                logger.debug('error talking to ualpn on %s: %s', socket_path, str(e))
                raise errors.PluginError('Error talking to ualpn on {0}: {1}'.format(
                    socket_path, str(e))) from None
                
            if response.startswith('OK'):
                logger.debug('ualpn: removed auth %s', achall.domain)
            else:
                logger.debug('ualpn: error removing auth %s: %s', achall.domain, response)
                raise errors.PluginError('Error removing auth for {0} from ualpn: {1}'.format(
                    achall.domain, response)) from None
 
