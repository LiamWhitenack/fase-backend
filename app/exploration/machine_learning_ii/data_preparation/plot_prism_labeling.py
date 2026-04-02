from app.crud.read.contracts_for_ml import contracts_for_ml
from app.exploration.machine_learning_ii.data_preparation.basic import (
    add_polynomial_structure,
)
from app.exploration.machine_learning_ii.data_preparation.constants import (
    OUTPUT_DIR,
    POSITION_COL,
)

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

    # # prepared = prepare_data(df)

    # print("Raw shape:", df.shape)
    # print("Transformed matrix shape:", prepared.transformed_matrix.shape)

    # plot_target_distributions(prepared.target_raw, prepared.target_log)

    # # Add a controlled amount of nonlinear structure for mining / clustering.
    # X_poly, poly_feature_names = add_polynomial_structure(
    #     prepared.transformed_matrix,
    #     prepared.transformed_feature_names,
    #     max_base_features=12,
    # )
    # print("Polynomial matrix shape:", X_poly.shape)

    # prism_angle = plot_pca_prism(
    #     X_poly,
    #     title="Prism Fan Representation From Apex",
    #     filename="prism_fan_continuous.png",
    #     use_angle_bins=False,
    # )

    # if POSITION_COL in prepared.features_engineered.columns:
    #     plot_position_overlay(
    #         X_poly,
    #         prepared.features_engineered[POSITION_COL],
    #         filename="pca_position_overlay.png",
    #     )

    # print("\nSaved outputs to:", OUTPUT_DIR.resolve())
    # print("Files created:")
    # for path in sorted(OUTPUT_DIR.glob("*")):
    #     print(" -", path.name)


if __name__ == "__main__":
    main()
