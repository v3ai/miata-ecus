# Added to rusEFI's unit-test build when BOARD_DIR points here (see firmware/README.md, "Simulation tests").
# Runs this board's real configuration code (miata_board.cpp) inside rusEFI's engine simulator.
TESTS_SRC_CPP += $(BOARD_DIR)/miata_board.cpp \
	$(BOARD_DIR)/tests/test_miata_ecu.cpp
INCDIR += $(BOARD_DIR)
