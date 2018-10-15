import time

from CUFLS_lib.rtds_talker import RtdsTalker

RTDS_IP = "192.168.1.102"
RTDS_PORT = 7571 # Node 01

if __name__ == '__main__':

    # == Init
    rconn = RtdsTalker(RTDS_IP, RTDS_PORT)

    # print(rconn.recv_bufsize)
    # print(RtdsTalker.recv_bufsize)

    # == Connect
    rconn.connect_rtds()
    # rconn.rtds_socket.close() # @TODO

    # == Send msg
    msg_str = 'Start;'
    rconn.send_message(msg_str)

    # == Receive msg
    # msg_bstr = rconn.receive_message
    # print(msg_bstr)

    # == Read meter
    mname_str = 'F2'
    mname_prefix = 'F'

    val = rconn.read_meter(mname_str, mname_prefix)
    print(val)

    # == Read multiple meters
    mnames_list = ['F{}'.format(id) for id in range(2,5)]
    mnames_prefixes_list = ['F']*(5-2)

    vals_list = rconn.read_multi_meters(mnames_list, mnames_prefixes_list)
    print(vals_list)

    # == Read multiple meters with the same prefix
    mname_prefix = 'F'
    id_range = range(2,5)

    vals_list = rconn.read_multi_meters_same_prefix(mname_prefix, id_range)
    print(vals_list)

    # == Set slider
    rconn.set_slider('L2-P',18.5)
    rconn.set_slider('L2-Q',9.5)
