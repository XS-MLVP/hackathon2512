TIMES ?= 1
VTARGET ?= bug_file/*.v;origin_file/*.v
N ?= 1
WORKSPACE ?= output
RESULT ?= result
DUTDIR ?= dutcache

comma := ;
T_LIST := $(subst $(comma), ,$(strip $(VTARGET)))
$(info >>> VTARGET_LIST is [$(T_LIST)])

DUT_NAME := $(firstword $(subst _, ,$(notdir $(DUT_FILE))))
DUT_BASE := $(basename $(notdir $(DUT_FILE)))

define RANDOM_PORT
	while true; do \
		port=$$(shuf -i 1024-65535 -n 1); \
		if ss -lntu | awk -v port=$${port} 'NR > 1 {split($$5,a,":"); if (a[length(a)] == port) exit 0} END {exit 1}'; then \
			continue; \
		fi; \
		echo $${port}; \
		break; \
	done
endef

PORT ?= $(shell $(call RANDOM_PORT))
PORT := $(PORT)
OLDPORT ?= 5000
CONTINUE ?= false
##########################################################################

clean:
	@rm -rf $(WORKSPACE)
	echo "clean $(WORKSPACE)"

clean_all: clean
	@rm -rf $(RESULT)
	@rm -rf $(DUTDIR)
	echo "clean $(RESULT) $(DUTDIR)"

init:
	@mkdir -p $(WORKSPACE)/$(PORT)
	@mkdir -p $(RESULT)/$(PORT)
	@mkdir -p $(DUTDIR)
	@if [ "$(CONTINUE)" = "false" ]; then \
		echo ">>> remove $(WORKSPACE)/$(PORT)/*" \
		rm -rf $(WORKSPACE)/$(PORT)/*; \
	fi

build_one_dut:
	@if [ ! -d "$(DUTDIR)/$(DUT_BASE)/$(DUT_NAME)" ]; then \
	  picker export $(DUT_FILE) --rw 1 --sname $(DUT_NAME) \
	    --tdir $(DUTDIR)/$(DUT_BASE)/ -c -w /tmp/$(DUT_BASE)_$(PORT).fst; \
	fi

build_dut_cache:
	@for p in $(T_LIST); do \
		for m in `find $$p`; do \
			$(MAKE) build_one_dut DUT_FILE=$$m DUTDIR=$(DUTDIR) PORT=$(PORT); \
		done; \
	done

run_list_mcp:
	@for p in $(T_LIST); do \
		for m in `find $$p`; do \
			$(MAKE) run_one_mcp DUT_FILE=$$m N=$$N PORT=$(PORT); \
		done; \
	done

run_seq_mcp:
	@i=1; \
	while [ $$i -le $(TIMES) ]; do \
	  $(MAKE) run_list_mcp N=$$i VTARGET=$(VTARGET) PORT=$(PORT); \
	  i=$$((i+1)); \
	done
	@echo "`date`: All runs completed." >> $(RESULT)/$(PORT)/run_log.txt
	@echo true > $(WORKSPACE)/$(PORT)/all_complete.txt

run_one_mcp: init
	@echo "`date`: " $(N) $(DUT_FILE) ">>>>>" $(DUT_NAME) ">>>>" $(DUT_BASE) ">>>>" $(PORT) >> $(RESULT)/$(PORT)/run_log.txt
	$(MAKE) build_one_dut DUT_FILE=$(DUT_FILE) DUT_NAME=$(DUT_NAME) DUT_BASE=$(DUT_BASE) DUTDIR=$(DUTDIR) PORT=$(PORT)
	@cp -r $(DUTDIR)/$(DUT_BASE)/$(DUT_NAME) $(WORKSPACE)/$(PORT)/
	@cp spec/$(DUT_NAME)*.md $(WORKSPACE)/$(PORT)/$(DUT_NAME)/
	@ucagent $(WORKSPACE)/$(PORT)/ $(DUT_NAME) -s -hm \
	  --tui --mcp-server-no-file-tools --no-embed-tools -eoc --mcp-server-port $(PORT) $(UCARGS)
	@cp -r $(WORKSPACE)/$(PORT) $(RESULT)/$(PORT)/RUN_$(N)_$(DUT_BASE)
	@echo "Waiting for DUT completion signal..."
	@while [ ! -f "$(WORKSPACE)/$(PORT)/dut_complete.txt" ]; do \
		sleep 5; \
	done

run_seq_cagent:
	@while true; do \
	  if [ -e "$(WORKSPACE)/$(PORT)/all_complete.txt" ]; then \
	    exit 0; \
	  fi; \
	  $(MAKE) run_one_cagent PORT=$(PORT); \
	done

run_one_cagent:
	@while [ ! -e "$(WORKSPACE)/$(PORT)/Guide_Doc/dut_fixture.md" ] || \
	       [ -e "$(WORKSPACE)/$(PORT)/dut_complete.txt" ]; do \
	  sleep 5; \
	  if [ -e "$(WORKSPACE)/$(PORT)/all_complete.txt" ]; then \
	    exit 0; \
	  fi; \
	done
	# Run iFlow CLI
	#  You can modify the corresponding startup code according to different Code Agent
	mkdir -p $(WORKSPACE)/$(PORT)/.iflow
	cp ~/.iflow/settings.json $(WORKSPACE)/$(PORT)/.iflow/settings.json
	sed -i "s/$(OLDPORT)\/mcp/$(PORT)\/mcp/" $(WORKSPACE)/$(PORT)/.iflow/settings.json
	(sleep 10; tmux send-keys `ucagent --hook-message cagent_init`; sleep 1; tmux send-keys Enter)&
	cd $(WORKSPACE)/$(PORT) && npx -y @iflow-ai/iflow-cli@latest -y && (echo true > dut_complete.txt)
	@echo "`date`: DUT iflow execution completed." >> $(RESULT)/$(PORT)/run_log.txt

run:
	tmux kill-session -t hk_batch_cagent_session_$(PORT) || true
	tmux new-session -d -s hk_batch_cagent_session_$(PORT)
	tmux send-keys -t hk_batch_cagent_session_$(PORT):0.0 \
	   "make run_seq_mcp PORT=$(PORT) OLDPORT=$(OLDPORT) WORKSPACE=$(WORKSPACE) RESULT=$(RESULT) \
	   TIMES=$(TIMES) VTARGET=$(VTARGET)" C-m
	tmux split-window -h -t hk_batch_cagent_session_$(PORT):0.0
	tmux send-keys -t hk_batch_cagent_session_$(PORT):0.1 \
	   "make run_seq_cagent PORT=$(PORT) OLDPORT=$(OLDPORT) WORKSPACE=$(WORKSPACE) RESULT=$(RESULT)" C-m
	tmux attach-session -t hk_batch_cagent_session_$(PORT)
