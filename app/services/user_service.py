from app.schemas.user_schema import UserResponse


class UserService:
    def get_current_user_data(current_user):
        """
        Service untuk mendapatkan data user yang sedang login
        """
        try:
            # Konversi user ke response schema
            user_data = UserResponse.model_validate(current_user)

            # Tambahkan data tambahan jika diperlukan
            response_data = {"success": True, "user": user_data.model_dump()}

            # Jika user adalah buyer, tambahkan data buyer_profile
            if (
                current_user.role
                and current_user.role.value == "buyer"
                and current_user.buyer_profile
            ):
                response_data["buyer_profile"] = {
                    "id": str(current_user.buyer_profile.id),
                    "username": current_user.buyer_profile.username,
                    "address": current_user.buyer_profile.address,
                    "phone_number": current_user.buyer_profile.phone_number,
                    "location_lat": current_user.buyer_profile.location_lat,
                    "location_lng": current_user.buyer_profile.location_lng,
                }

            # Jika user adalah seller, tambahkan data seller_profile
            elif (
                current_user.role
                and current_user.role.value == "seller"
                and current_user.seller_profile
            ):
                response_data["seller_profile"] = {
                    "shop_name": current_user.seller_profile.shop_name,
                    "description": current_user.seller_profile.description,
                    "logo_url": current_user.seller_profile.logo_url,
                    "cover_image_url": current_user.seller_profile.cover_image_url,
                    "location_address": current_user.seller_profile.location_address,
                    "phone_number": current_user.seller_profile.phone_number,
                    # Bisa ditambahkan data lainnya sesuai kebutuhan
                }

            # Jika user adalah admin, tambahkan info admin langsung
            elif current_user.role and current_user.role.value == "admin":
                response_data["admin_info"] = {
                    "email": current_user.email,
                    "role": "admin",
                    "created_at": (
                        current_user.created_at.isoformat()
                        if current_user.created_at
                        else None
                    ),
                }

            return response_data, 200

        except Exception as e:
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500
