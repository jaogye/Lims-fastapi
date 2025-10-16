function hashcode = getHashCode(code,password)
% validate user names and provide rights based on thier levels
% pass code is hashed
sha256hasher = System.Security.Cryptography.SHA256Managed;
p1_hash = uint8(sha256hasher.ComputeHash(uint8(char( code ))));
hashcode = reshape(dec2hex(typecast(p1_hash,'uint8')),1,[]);

end 
