if ( ! $?__Init_Default_Modules )  then
  setenv __Init_Default_Modules 1
  if ( ! $?LMOD_SYSTEM_DEFAULT_MODULES ) then
    setenv LMOD_SYSTEM_DEFAULT_MODULES "{{ role_lmod_syshost }}"
  endif
  module --initial_load restore
else
  module refresh
endif
