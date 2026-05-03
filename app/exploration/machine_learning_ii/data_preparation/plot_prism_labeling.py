from app.exploration.machine_learning_ii.data_preparation.default import prepare_data
from app.crud.read.contracts_for_ml import contracts_for_ml
from app.exploration.machine_learning_ii.data_preparation.basic import (
    add_polynomial_structure,
)
from app.exploration.machine_learning_ii.data_preparation.constants import OUTPUT_DIR

# from app.exploration.machine_learning_ii.data_preparation.position_labeling_helper import (
#     plot_pca_prism,
#     plot_position_overlay,
# )
# from app.exploration.machine_learning_ii.data_preparation.default import prepare_data
from app.exploration.machine_learning_ii.data_preparation.transformation import (
    plot_target_distributions,
)


def main() -> None:
    df = contracts_for_ml()

    prepared = prepare_data(df)

    print("Raw shape:", df.shape)
    print("Transformed matrix shape:", prepared.transformed_matrix.shape)

    plot_target_distributions(prepared.target_raw, prepared.target_log)

    print("\nSaved outputs to:", OUTPUT_DIR.resolve())
    print("Files created:")
    for path in sorted(OUTPUT_DIR.glob("*")):
        print(" -", path.name)


if __name__ == "__main__":
    main()
