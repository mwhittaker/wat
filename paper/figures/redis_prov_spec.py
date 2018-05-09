 def get_prov(T: List[Request], i: GetRequest):
   for a in reversed(T):
     if isinstance(a, SetRequest) and a.key == i.key:
       return {[a]}
   return {[]}
