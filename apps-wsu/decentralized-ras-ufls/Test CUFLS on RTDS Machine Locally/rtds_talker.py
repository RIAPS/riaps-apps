import socket


def parse_message(msg_bstr):
    msg_str = msg_bstr.decode()
    pmsg_str = msg_str.split(' ')[2]
    pmsg_float = float(pmsg_str)
    return pmsg_float

class RtdsTalker(object):
    """
    An interface that collects measurements from the RTDS, 
    and sends control commands back to the RTDS.
    
    It requires the IP and Port of the RTDS for initialization. 
    """

    recv_bufsize = 128 # @TODO

    def __init__(self, rtds_ip, rtds_port):
        """
        Initialize a rtds talker.
        Inputs:
        - rtds_ip: A string giving the IP of the RTDS
        - rtds_port: An integer giving the associated Port information
        """

        self.rtds_ip = rtds_ip
        self.rtds_port = rtds_port
        self.rtds_socket = socket.socket() # use default params: socket.AF_INET & socket.SOCK_STREAM

    def connect_rtds(self):
        """
        Connect to the RTDS.
        """
        print('Connecting to RTDS (IP: {}, Port: {})'.\
                format(self.rtds_ip, self.rtds_port))
        self.rtds_socket.connect((self.rtds_ip, self.rtds_port))
        print('Connection is established successfully.')
        # return True # @TODO

    def disconnect_rtds(self):
        self.rtds_socket.close()

    def send_message(self, msg_str):
        self.rtds_socket.send(msg_str.encode())

    def receive_message(self):
        msg_bstr = self.rtds_socket.recv(RtdsTalker.recv_bufsize)
        return msg_bstr

    def read_meter(self, mname_str, mname_prefix):
        tf_str = 'temp_float'
        ts_str = 'temp_string'

        cmd1_str = tf_str + ' = MeterCapture("' + mname_str + '");'
        cmd2_str = 'sprintf(' + ts_str + ', "' + mname_str + ' = %f END", ' + tf_str + ');'
        cmd3_str = 'ListenOnPortHandshake(' + ts_str + ');'

        self.send_message(cmd1_str)
        self.send_message(cmd2_str)
        self.send_message(cmd3_str)

        meter_msg_bstr = ''.encode()

        while (mname_prefix not in meter_msg_bstr.decode()):
            meter_msg_bstr = self.receive_message()
            # print(meter_msg_bstr) # @For debug

        meter_value = parse_message(meter_msg_bstr)
        return meter_value

    def read_multi_meters(self, mnames_list, mnames_prefixes_list):
        meters_vals_list = list()

        for mname, mname_prefix in zip(mnames_list, mnames_prefixes_list):
            meter_value = self.read_meter(mname, mname_prefix)
            meters_vals_list.append(meter_value)

        return meters_vals_list

    def read_multi_meters_same_prefix(self, mname_prefix, id_range):
        format_str = mname_prefix + '{}'
        mnames_list = [format_str.format(id) for id in id_range]
        mnames_prefixes_list = ['F'] * len(id_range)

        meters_vals_list = self.read_multi_meters(mnames_list, mnames_prefixes_list)

        return meters_vals_list

    def set_slider(self, slider_name, slider_val):
        cmd_str = 'SetSlider "%s" = %f;' % (slider_name, slider_val)
        cmd_bstr = cmd_str.encode()
        self.write_cmd(cmd_bstr)

    def write_cmd(self, cmd_bstr):
        self.rtds_socket.send(cmd_bstr)
