import function_calling


while True:
    try:
        function_calling.prompt_step()
    except KeyboardInterrupt:
        import pdb
        pdb.set_trace()
