def load_fw_or_die():
	fw = System.Environment.GetEnvironmentVariable("FW")
	if fw:
		print('log "Loading {}..." 1; `$bin=@{}`'.format(fw, fw))
	else:
		print('log "No firmware loaded! Please set the FW environment variable!" 3; quit')