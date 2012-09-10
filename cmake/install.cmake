if (ROS_ELECTRIC_FOUND OR ROS_FUERTE_FOUND)
# install the include folder
install(DIRECTORY ${PROJECT_SOURCE_DIR}/include/
        DESTINATION include
        COMPONENT main
)

# install the share folder
install(DIRECTORY ${CMAKE_BINARY_DIR}/share/test
        DESTINATION share/${PROJECT_NAME}
        COMPONENT main
        USE_SOURCE_PERMISSIONS
)
endif()

if (ROS_ELECTRIC_FOUND)
# install the applications
install(PROGRAMS ${PROJECT_SOURCE_DIR}/apps/detection
                 ${PROJECT_SOURCE_DIR}/apps/training 
        DESTINATION bin
)

install(FILES ${PROJECT_SOURCE_DIR}/apps/roscompat.py
        DESTINATION bin
)
endif()

if (ROS_FUERTE_FOUND)
# install the applications
install(PROGRAMS ${PROJECT_SOURCE_DIR}/apps/detection
                 ${PROJECT_SOURCE_DIR}/apps/training
        DESTINATION share/${PROJECT_NAME}/bin
)

install(FILES ${PROJECT_SOURCE_DIR}/apps/roscompat.py
        DESTINATION share/${PROJECT_NAME}/bin
)
install(FILES ${PROJECT_SOURCE_DIR}/manifest.xml
        DESTINATION share/${PROJECT_NAME}
)
endif()

if (ROS_GROOVY_OR_ABOVE_FOUND)
# install the include folder
install(DIRECTORY ${PROJECT_SOURCE_DIR}/include/object_recognition_core/
        DESTINATION ${CATKIN_PROJECT_INCLUDE_DESTINATION}
        COMPONENT main
)
 
# install the share folder
install(DIRECTORY ${CATKIN_BUILD_PREFIX}/${CATKIN_PROJECT_SHARE_DESTINATION}/test
        DESTINATION ${CATKIN_PROJECT_SHARE_DESTINATION}
        COMPONENT main
        USE_SOURCE_PERMISSIONS
)

# install the applications
install(PROGRAMS ${PROJECT_SOURCE_DIR}/apps/detection
                 ${PROJECT_SOURCE_DIR}/apps/training
        DESTINATION ${CATKIN_PROJECT_BIN_DESTINATION}
)

install(FILES ${PROJECT_SOURCE_DIR}/apps/roscompat.py
        DESTINATION ${CATKIN_PROJECT_BIN_DESTINATION}
)
endif()
